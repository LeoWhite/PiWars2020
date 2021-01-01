#! /usr/bin/python3
from MotorBase import MotorBase
import sys
import redboard

# A Motor class used for abstraction purposes

class MotorRedBoard(MotorBase):
    def __init__(self):
        print("RedBoard init")
        self._redBoard = redboard.RedBoard()

    def _left(self, speed):
        """ Sets the speed of the left motor, in the range of -1.0 to 1.0"""
        #print("_left"+str(speed))
        self._redBoard.m1 = speed


    def _right(self, speed):
        """ Sets the speed of the right motor, in the range of -1.0 to 1.0"""
        #print("_right"+str(speed))
        self._redBoard.m0 = speed
        

        
if __name__ == '__main__':
   import time

   MotorRedBoard = MotorRedBoard()
   MotorRedBoard.set_left(1.0)
   time.sleep(1)
   MotorRedBoard.set_left(-1.0)
   time.sleep(1)
   MotorRedBoard.stop_all()
