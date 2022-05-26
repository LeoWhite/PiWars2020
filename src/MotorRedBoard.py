#! /usr/bin/python3
from MotorBase import MotorBase
import sys
import redboard
import yaml

# Defines and constants
YAML_CONFIG_FILE='../config/config.json'

# Read in the YAML config file
with open(YAML_CONFIG_FILE, 'r') as yaml_data_file:
    config = yaml.safe_load(yaml_data_file)

# A Motor class used for abstraction purposes

class MotorRedBoard(MotorBase):
    def __init__(self):
        print("RedBoard init")
        self._redBoard = redboard.RedBoard()
        self._redBoard.config=config["RedBoard"]


    def _left(self, speed):
        """ Sets the speed of the left motor, in the range of -1.0 to 1.0"""
        #print("_left"+str(speed))
        self._redBoard.m0 = self._redBoard.m2 = speed


    def _right(self, speed):
        """ Sets the speed of the right motor, in the range of -1.0 to 1.0"""
        #print("_right"+str(speed))
        self._redBoard.m1 = self._redBoard.m3 = speed
        
    def _set_servo(self, servo, range):
      if servo == 0:
        self._redBoard.s20 = range
      elif servo == 1:
        self._redBoard.s21 = range
        
if __name__ == '__main__':
   import time

   MotorRedBoard = MotorRedBoard()
   MotorRedBoard.set_left(0.25)
   time.sleep(1)
   MotorRedBoard.set_left(-1.0)
   time.sleep(1)
   MotorRedBoard.stop_all()
   MotorRedBoard.set_right(1.0)
   time.sleep(1)
   MotorRedBoard.set_right(-1.0)
   time.sleep(1)
   MotorRedBoard.stop_all()
