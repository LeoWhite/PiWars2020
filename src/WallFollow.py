import atexit
import json
import queue
import socket

from pi_controller import PIController
from threading import Thread

from MotorZeroBorg import MotorZeroBorg as Motor
#from MotorRedBoard import MotorRedBoard as Motor

# Defines and constants
JSON_CONFIG_FILE='../config/tb2.json'
MIN_SIDE_DISTANCE=100

# Thread that monitors for UDP packets in the background
class UDPMonitorThread(Thread):
    def __init__(self, UDPAddress, messageQueue):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(UDPAddress)
        self._messageQueue = messageQueue

    def run(self):
        while True:
          data, addr = self.socket.recvfrom(1024)

          message = json.loads(data)

          if message["name"] == "right":
            # Update list, signal main loop?
            self._messageQueue.put_nowait(message)


# Attemps to follow a wall
class WallFollowBehaviour(object):
  def __init__(self, Motor, speed):
    # Configure the motors
    self._motor = Motor

    # Create a queue for passing messages
    self._messageQueue = queue.Queue()

    # Cache the base speed
    self._speed = speed
    
    # Read in the JSON config file
    with open(JSON_CONFIG_FILE) as json_data_file:
        self._config = json.load(json_data_file)

    # Work out the UDP Address to listen on
    udpAddress = ( self._config["ToF"]["udp"]["address"], int(self._config["ToF"]["udp"]["port"]) )

    # Launch the UDP/ToF monitor
    self._tofMonitor = UDPMonitorThread(udpAddress, self._messageQueue)
    self._tofMonitor.daemon = True
    self._tofMonitor.start()

    # Make sure we release it at exit
    atexit.register(self.shutdown)

  def run(self):
    # Create a PID controller
    controller = PIController(proportional_constant=0.01, integral_constant=0, windup_limit=0.5)

    # Run for ever
    running = True
    
    # Throw away the first few results, to allow the sensor to settle down.
    count = 3
    while count > 0:
      message = self._messageQueue.get(True)
      count = count - 1

    # Set the base speed
    self._motor.set_left(self._speed)
    self._motor.set_right(self._speed)

    # and start processing results
    while running:
      # Wait for the next distance update
      message = self._messageQueue.get(True)

      # Calculate the error and update the PID values
      error = message['distance'] - MIN_SIDE_DISTANCE
      adjustment = controller.get_value(error)
      print(message['distance'],"e:",error, " a:", adjustment, "s:", self._speed - adjustment)

      # Update motors
      self._motor.set_right(self._speed - adjustment)

      # Check front sensor? Stop when we get close to the wall


  def shutdown(self):
      self._motor.stop_all()


if __name__ == '__main__':
  behaviour=WallFollowBehaviour(Motor(), 0.5)
  behaviour.run()
  