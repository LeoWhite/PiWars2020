import atexit
import json
import queue
import socket
import yaml
import time

from Tom import Tom
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
TROUGH_SAFE_DISTANCE=200
TROUGH_LOADING_DISTANCE=50
ColourStruct = namedtuple("ColourStruct", "colour low high")

RED=ColourStruct("red", np.array([160,100,50]), np.array([179,255,255]))
GREEN=ColourStruct("green", np.array([60-20,100,50]), np.array([60+20,255,255]))
BLUE=ColourStruct("blue", np.array([100,100,50]), np.array([120,255,255]))


# The planned route
# 1 = Cattle trough 1 (Green)
# 2 - Cattle trough 2 (Blue)
# 3 - Cattle trough 3 (Red)
# L - Turn left 90
# R - Turn right 90
# B - Back up
# U - U-turn
# A - Activate feeder
# 0 - Barn
# FULL ROUTE="U1ABL2ABR3AU"
ROUTE="1ABL2ABR3ABU0UR"
food_delivery_time=1.5
food_delivery_extra=0.5



# Attempts to feed Hungry Cattle!
class HungryCattle(object):
  def __init__(self, tom, speed):
    # Configure the motors
    self._tom = tom

    # Cache the base speed
    self._speed = speed
    
        
  def run(self):
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

  def driveCallback(self, radius):

    # Read in the current distance
    distance = self._tom.readToFSensor("front_left")

    print("Distances: ", distance)
    
    # Is it an invalid request?
    if distance < 0:
      print("Invalid ToF sensor setup")
      # Abort driving now
      return False
    # Distance too far, or out of date
    elif distance == 0:
      print("Invalid distance, continuing")
      # Continue for now
      # IMPROVE: Abort after X failures
      return True
    # Not yet close enough?
    elif distance > TROUGH_SAFE_DISTANCE:
      print("Still driving")
      return True
     
    print("Stopping")
    return False

  def turn_90_degrees(self, direction):
    # Default speed = turn right
    speed = self._speed * 2
    
    # Do we want to go left?
    if direction == 1:
      speed = -speed
    
    self._tom.set_left(speed)
    self._tom.set_right(-speed)
    time.sleep(1)
    self._tom.stop_all()

  def turn_180_degrees(self):
    # Default speed = turn right
    speed = self._speed * 2
    
    self._tom.set_left(speed)
    self._tom.set_right(-speed)
    time.sleep(1.75)
    self._tom.stop_all()
        
  def approach_trough(self, colour):
    print("Seraching for colour {}".format(colour.colour))


    # Now drive to the colour
    self._tom.aim_at_colour(colour.low, colour.high, 1, self._speed)

    print("aim complete")

    # Drive forwards for a bit, as if the distance is too far we get sensor reflection
    while self._tom.readToFSensor("front_left") < 300:
      self._tom.set_left(self._speed)
      self._tom.set_right(self._speed)
      time.sleep(0.05)
      
    print("driving to colour")

    self._tom.drive_to_colour(self.driveCallback, colour.low, colour.high, self._speed)
    
    # Creep forwards
    while self._tom.readToFSensor("front_left") > TROUGH_LOADING_DISTANCE:
      print("Crreeping {}".format(self._tom.readToFSensor("front_left")))
      self._tom.set_left(0.15)
      self._tom.set_right(0.15)
      time.sleep(0.1)
    
    print("Creeping done")
    self._tom.set_left(-0.15)
    self._tom.set_right(-0.15)
    time.sleep(0.05)
    self._tom.stop_all()
      
  def go_home(self):
    print("Heading home")


    # Now drive to the colour
    self._tom.aim_at_colour(RED.low, RED.high, 1, self._speed)

    # Drive forwards for a bit, as if the distance is too far we get sensor reflection
    while self._tom.readToFSensor("front_left") < 300:
      self._tom.set_left(self._speed)
      self._tom.set_right(self._speed)
      time.sleep(0.05)
      

    self._tom.drive_to_colour(self.driveCallback, RED.low, RED.high, self._speed)
    
    print("Creeping done")
    self._tom.set_left(-0.15)
    self._tom.set_right(-0.15)
    time.sleep(0.05)
    self._tom.stop_all()
      
    
  def deliver_food(self, step):
    global food_delivery_time

    # Open hooper
    self._tom.set_servo(1, 1);

    # Wait for feed to leave
    time.sleep(food_delivery_time)
  
    # Close hopper
    self._tom.set_servo(1, -1);
    
    # Increase for the next one (As less food)
    food_delivery_time += food_delivery_extra
    
    # Allow time for hopper to close
    time.sleep(0.5)

  def processStep(self, step):
    if step == "L" :
        self.turn_90_degrees(1)
    elif step == "R" :
        self.turn_90_degrees(0)
    elif step == "U" :
        self.turn_180_degrees()
    elif step == "1" :
        self.approach_trough(GREEN)
    elif step == "2" :
        self.approach_trough(BLUE)
    elif step == "3" :
        self.approach_trough(RED)
    elif step == "0" :
        self.go_home()
    elif step == "A" :
        self.deliver_food(step)
    elif step == "B" :
      self._tom.set_left(-self._speed)
      self._tom.set_right(-self._speed)
      time.sleep(0.5)
      self._tom.stop_all()
    else:
      print("Unknown step ["+step+"]")





if __name__ == '__main__':
  behaviour=HungryCattle(Tom(), 0.35)
  behaviour.run()
  
