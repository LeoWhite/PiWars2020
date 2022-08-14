import atexit
import yaml
import json
import socket
import time

from pi_controller import PIController
from MotorRedBoard import MotorRedBoard as Motor
from collections import namedtuple
from threading import Thread

# Include camera and openCV for image processing
import cv2
import numpy as np
import pi_camera_stream
    
# Defines and constants
YAML_CONFIG_FILE='../config/config.yaml'
TOF_TIMEOUT=0.5
SensorStruct = namedtuple("SensorStruct", "distance time")

# Thread that monitors for UDP packets in the background
class UDPMonitorThread(Thread):
    def __init__(self, UDPAddress, tofSensors):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(UDPAddress)
        self._tofSensors = tofSensors

    def run(self):
        while True:
          data, addr = self.socket.recvfrom(1024)

          message = json.loads(data)

          # Is it a sensor we care about?
          if message["name"] in self._tofSensors.keys():
            self._tofSensors[message["name"]] = SensorStruct(message["distance"], message["time"])
          else:
            print("Unknown sensor "+message["name"])

    
# Allows direct manual control of TB2
class Tom(Motor):
  correct_radius = 120
  center = 160

  _debug = True
  
  def __init__(self):
    Motor.__init__(self)
    
    # Read in the YAML config file
    with open(YAML_CONFIG_FILE, 'r') as yaml_data_file:
      self._config = yaml.safe_load(yaml_data_file)

    # Build up a list of the sensors
    self._tofSensors={}
    for address in self._config['ToF']['sensors']:
      self._tofSensors[address["name"]] = SensorStruct(-1, 0)
  
    # Do we have any?
    if len(self._tofSensors) > 0:
      print("Setting up ToF monitor")
      
      # Work out the UDP Address to listen on
      udpAddress = ( self._config["ToF"]["udp"]["address"], self._config["ToF"]["udp"]["port"] )

      # Launch the UDP/ToF monitor
      self._tofMonitor = UDPMonitorThread(udpAddress, self._tofSensors)
      self._tofMonitor.daemon = True
      self._tofMonitor.start()

      # Wait for the sensors to settle down.
      print("Waiting for ToF sensors to settle")
      firstSensor = list(self._tofSensors.keys())[0]
      while self._tofSensors[firstSensor].distance <= 0:
        time.sleep(0.1)


    # Start the camera
    # IMPROVE: Only trigger if needed?
    self._camera = pi_camera_stream.setup_camera()


    # Make sure we release everything at exit
    atexit.register(self.shutdown)

        
  def shutdown(self):
      self.stop_all()

  def find_object(self, original_frame, low_range, high_range):
      """Find the largest enclosing circle for all contours in a masked image.
      Returns: the masked image, the object coordinates, the object radius"""
      frame_hsv = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
      masked = cv2.inRange(frame_hsv, low_range, high_range)

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


  def process_frame(self, frame_orig, low_range, high_range):
      # Crop the frame to avoid distractions
      frame = frame_orig[80:200, 0:320]

      
      #frame = frame_orig
      # Find the largest enclosing circle
      masked, coordinates, radius = self.find_object(frame, low_range, high_range)
      
      if self._debug:
        # Now back to 3 channels for display
        processed = cv2.cvtColor(masked, cv2.COLOR_GRAY2BGR)
        # Draw our circle on the original frame, then display this
        cv2.circle(frame, coordinates, radius, [255, 0, 0])
        cv2.imshow('output',frame)
        cv2.waitKey(1)
      
      # Yield the object details
      return coordinates, radius


  def aim_at_colour(self, low_range, high_range, direction=1, speed=0.5):
    
      # start the loop
      for frame in pi_camera_stream.start_stream(self._camera):
        # Process the frame
        (x, y), radius = self.process_frame(frame, low_range, high_range)
        
          
        # Work out how far from the center it is
        direction_error = self.center - x

        if self._debug:
          print("radius: {} direction_error: {}".format(radius, direction_error))

        # Have we found nothing?
        if radius == 0:
          # Do we want to go left?
          if direction == 1:
            targetSpeed = -speed
          else:
            targetSpeed = speed
            
          self.set_left(targetSpeed)
          self.set_right(-targetSpeed)
          
        # Too far left?
        elif direction_error > 5:
            # Move left 
            targetSpeed = -speed
              
            # Now produce left and right motor speeds
            self.set_left(targetSpeed)
            self.set_right(-targetSpeed)
        # Too far right?
        elif direction_error < -5:
            # Move right
            targetSpeed = speed
              
            # Now produce left and right motor speeds
            self.set_left(targetSpeed)
            self.set_right(-targetSpeed)
        # Close enough, so stop
        else:
            print("aim_at_colour:Stopping")
            self.stop_all()
            break
  
  
  def drive_to_colour(self, callback, low_range, high_range, speed=0.75):
      # Direction controller
      controller = PIController(proportional_constant=0.0015, integral_constant=0.0000, windup_limit=40)

      # start the loop
      for frame in pi_camera_stream.start_stream(self._camera):
        # Process the frame
        (x, y), radius = self.process_frame(frame, low_range, high_range)
        
        # Time to exit?
        if callback(radius) == False:
          break
          
        # The size is the first error
        radius_error = self.correct_radius - radius
        #speed_value = speed_pid.get_value(radius_error)
        # And the second error is the based on the center coordinate.
        direction_error = self.center - x
        direction_value = controller.get_value(direction_error)
        
        if self._debug:
          print("radius: %d, radius_error: %d direction_error: %d, direction_value: %.2f speed %.2f" %
              (radius, radius_error, direction_error, direction_value, speed + direction_value))
        
        # Now produce left and right motor speeds
        self.set_left(speed - direction_value)
        self.set_right(speed + direction_value)

      print("drive_to_colour:Stopping")
      self.stop_all()
  
  # Reads in the latest distance of a named ToF sensor.
  # Returns -1 if unknown sensor
  # 0 if distance unknown (Too far for sensor to detect, or 
  # last reading to old
  def readToFSensor(self, name):
    # Is it a known 
    if name in self._tofSensors.keys():
      sensorDetails = self._tofSensors[name]
      
      # Is the distance still considered valid?
      if time.time() - sensorDetails.time <= TOF_TIMEOUT:
        return sensorDetails.distance
      else:
        print("Sensor data too old!")
        return 0
    
    # Unknown sensor
    return -1
    
  
