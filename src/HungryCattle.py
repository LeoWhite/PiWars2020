import atexit
import json
import queue
import socket
import yaml
import time

from pi_controller import PIController
from threading import Thread

from MotorRedBoard import MotorRedBoard as Motor
from collections import namedtuple

import cv2
import numpy as np
import pi_camera_stream
from pi_controller import PIController


# Defines and constants
YAML_CONFIG_FILE='../config/config.yaml'
MIN_SIDE_DISTANCE=100
ColourStruct = namedtuple("ColourStruct", "colour low high")

RED=ColourStruct("red", np.array([160,100,50]), np.array([179,255,255]))
GREEN=ColourStruct("green", np.array([60-20,100,50]), np.array([60+20,255,255]))
BLUE=ColourStruct("blue", np.array([100,100,50]), np.array([120,255,255]))


# The planned route
# 1 = Cattle trough 1 (Red)
# 2 - Cattle trough 2 (Blue)
# 3 - Cattle trough 3
# L - Turn left 90
# R - Turn right 90
# B - Back up
# U - U-turn
# A - Activate feeder
# 0 - Barn
# FULL ROUTE="U1ABL2ABR3AU"
ROUTE="LR"


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

          if message["name"] == "front_left":
            # Update list, signal main loop?
            self._messageQueue.put_nowait(message)


# Attempts to feed Hungry Cattle!
class HungeryCattle(object):
  def __init__(self, Motor, speed):
    # Configure the motors
    self._motor = Motor

    # Create a queue for passing messages
    self._messageQueue = queue.Queue()

    # Cache the base speed
    self._speed = speed
    
    # Read in the YAML config file
    with open(YAML_CONFIG_FILE, 'r') as yaml_data_file:
      self._config = yaml.safe_load(yaml_data_file)

    # Work out the UDP Address to listen on
    udpAddress = ( self._config["ToF"]["udp"]["address"], self._config["ToF"]["udp"]["port"] )

    # Launch the UDP/ToF monitor
    self._tofMonitor = UDPMonitorThread(udpAddress, self._messageQueue)
    self._tofMonitor.daemon = True
    self._tofMonitor.start()

    # Make sure we release it at exit
    atexit.register(self.shutdown)

    # Throw away the first few results, to allow the sensor to settle down.
    print("Waiting for ToF sensor to settle down")
    count = 3
    while count > 0:
      message = self._messageQueue.get(True)
      count = count - 1


    def find_object(self, original_frame):
        """Find the largest enclosing circle for all contours in a masked image.
        Returns: the masked image, the object coordinates, the object radius"""
        frame_hsv = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
        masked = cv2.inRange(frame_hsv, self.low_range, self.high_range)

        # Find the contours of the image (outline points)
        contour_image = np.copy(masked)
        contours, _ = cv2.findContours(contour_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # Find enclosing circles
        circles = [cv2.minEnclosingCircle(cnt) for cnt in contours]
        # Filter for the largest one
        largest = (0, 0), 0
        for (x, y), radius in circles:
            if radius > largest[1]:
                largest = (int(x), int(y)), int(radius)
        return masked, largest[0], largest[1]


    def process_frame(self, frame_orig):
        # Crop the frame
        frame = frame_orig[80:160, 0:320]
        
        #frame = frame_orig
        # Find the largest enclosing circle
        masked, coordinates, radius = self.find_object(frame)
        # Now back to 3 channels for display
        processed = cv2.cvtColor(masked, cv2.COLOR_GRAY2BGR)
        # Draw our circle on the original frame, then display this
        cv2.circle(frame, coordinates, radius, [255, 0, 0])
#        self.make_display(frame, processed)
        cv2.imshow('output',frame)
        cv2.waitKey(1)
        # Yield the object details
        return coordinates, radius
        
  def run(self):
    # start camera
    camera = pi_camera_stream.setup_camera()

    # Create a PID controller
    controller = PIController(proportional_constant=0.01, integral_constant=0, windup_limit=0.5)

    # Run for ever
    running = True
    
    # Set the base speed
    #self._motor.set_left(self._speed)
    #self._motor.set_right(self._speed)


    # Iterate over each direction
    for step in ROUTE:
      self.processStep(step)      


  def shutdown(self):
      self._motor.stop_all()

  def turn_90_degrees(self, direction):
    # Default speed = turn right
    speed = self._speed
    
    # Do we want to go left?
    if direction == 1:
      speed = -speed
    
    self._motor.set_left(speed)
    self._motor.set_right(-speed)
    time.sleep(0.5)
    self._motor.stop_all()
    
  def processStep(self, step):
    if step == "L" :
        self.turn_90_degrees(1)
    elif step == "R" :
        self.turn_90_degrees(0)
    else:
      print("Unknown step ["+step+"]")





if __name__ == '__main__':
  behaviour=HungeryCattle(Motor(), 0.5)
  behaviour.run()
  