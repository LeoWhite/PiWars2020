from approxeng.input.selectbinder import ControllerResource

import atexit
#from MotorZeroBorg import MotorZeroBorg as Motor
from MotorRedBoard import MotorRedBoard as Motor


# Allows direct manual control of TB2
class ManualDriveBehaviour(object):
  def __init__(self, Motor):
    self._motor = Motor
    self._lid = 0
    
    # Make sure we release it at exit
    atexit.register(self.shutdown)

  def run(self):
    # Run for ever
    running = True

    # Attempt to find a joystick
    with ControllerResource() as joystick:    
      while running and joystick.connected:
        presses = joystick.check_presses()

        if presses['cross']:
          print("cross pressed. Mode", self._lid)
          if self._lid == 0:
            self._lid = 1;
            self._motor.set_servo(0, 1);
            self._motor.set_servo(1, -1);
          else:
            self._lid = 0;
            self._motor.set_servo(0, -1);
            self._motor.set_servo(1, 1);
 

        left_y, right_y = joystick['ly', 'ry']
        #print("", left_y, "x", right_y)
        self._motor.set_left(left_y)
        self._motor.set_right(right_y)

        # Check for exit
        powerOff  = joystick['start']
        if powerOff is not None:
            if powerOff >= 3:
              print("Power off!")
              running = False


  def shutdown(self):
      self._motor.stop_all()


if __name__ == '__main__':
  behaviour=ManualDriveBehaviour(Motor())
  behaviour.run()
  
