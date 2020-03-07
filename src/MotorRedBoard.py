#! /usr/bin/python3
from MotorBase import MotorBase
import sys
sys.path.append('/home/pi/RedBoard')
import redboard

# A Motor class used for abstraction purposes

class MotorRedBoard(MotorBase):
    def __init__(self):
        # Redboard doesn't have any setup stage currently, so nothing to do here!
        print("RedBoard init")

    def _left(self, speed):
        """ Sets the speed of the left motor, in the range of -1.0 to 1.0"""
        print("_left"+str(speed))
        redboard.M2(speed * 100)


    def _right(self, speed):
        """ Sets the speed of the right motor, in the range of -1.0 to 1.0"""
        print("_right"+str(speed))
        redboard.M1(speed * 100)
        

        
if __name__ == '__main__':
   import time

   MotorRedBoard = MotorRedBoard()
   MotorRedBoard.set_left(1.0)
   time.sleep(1)
   MotorRedBoard.set_left(-1.0)
   time.sleep(1)
   MotorRedBoard.stop_all()
