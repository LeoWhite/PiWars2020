#! /usr/bin/python3
from MotorBase import MotorBase
import sys
sys.path.append('/home/pi/zeroborg')
import ZeroBorg3 as ZeroBorg

# A Motor class used for abstraction purposes

class MotorZeroBorg(MotorBase):
    def __init__(self):
        # As this is a stubbed out class there isn't anything we need to do here
        # Possibly define some max ranges or other globals
        self._zb = ZeroBorg.ZeroBorg()
        self._zb.i2cAddress = 0x41
        self._zb.Init()
        if not self._zb.foundChip:
            print("Failed to find Zeroborg!")
            sys.exit()
        self._zb.ResetEpo()

    def _left(self, speed):
        """ Sets the speed of the left motor, in the range of -1.0 to 1.0"""
        print("_left"+str(speed))
        self._zb.SetMotor1(speed)


    def _right(self, speed):
        """ Sets the speed of the right motor, in the range of -1.0 to 1.0"""
        print("_right"+str(speed))
        self._zb.SetMotor2(speed)
        

        
if __name__ == '__main__':
   import time

   MotorZeroBorg = MotorZeroBorg()
   MotorZeroBorg.set_left(1.0)
   time.sleep(1)
   MotorZeroBorg.set_left(-1.0)
   time.sleep(1)
   MotorZeroBorg.stop_all()
