#! /usr/bin/python3

# A Motor class used for abstraction purposes

class MotorBase(object):
    def __init__(self):
        # As this is a stubbed out class there isn't anything we need to do here
        # Possibly define some max ranges or other globals
        print("init")

    def set_left(self, speed):
        """ Sets the speed of the left motor, in the range of -1.0 to 1.0"""
        print("set_left"+str(speed))
        self._left(speed)


    def set_right(self, speed):
        """ Sets the speed of the right motor, in the range of -1.0 to 1.0"""
        print("set_right"+str(speed))
        self._right(speed)
        

    def stop_all(self):
        # Stops both motors
        print("set_stop")
        self.set_left(0.0)
        self.set_right(0.0)

    def _clip_speed(self, speed):
        if speed > 1.0:
            speed = 1.0
        elif speed < -1.0:
          speed = -1.0
        
        return speed
