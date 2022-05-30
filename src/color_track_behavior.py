import time

import cv2
import numpy as np

import atexit
#from MotorZeroBorg import MotorZeroBorg as Motor
from MotorRedBoard import MotorRedBoard as Motor


import pi_camera_stream
from pi_controller import PIController



class ColorTrackingBehavior(object):
    """Behavior to find and get close to a colored object"""
    def __init__(self, Motor):
        self._motor = Motor
        # Tuning values (Green)
        #self.low_range = (60-20, 100, 50)
        #self.high_range = (60+20, 255, 255)
        
        self.low_range = np.array([160,100,50])
        self.high_range = np.array([179,255,255])
        self.correct_radius = 120
        self.center = 160

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

        # direction pid - how far from the middle X is.
        direction_pid = PIController(proportional_constant=0.0015, integral_constant=0.0000, windup_limit=400)
            

        # warm up and servo move time
        time.sleep(0.1)

        print("Setup Complete")
        # Main loop
        for frame in pi_camera_stream.start_stream(camera):
            (x, y), radius = self.process_frame(frame)
            
            print("Coordes: %dx%d" % (x, y))
            
            if radius > 20:
                # The size is the first error
                radius_error = self.correct_radius - radius
                #speed_value = speed_pid.get_value(radius_error)
                # And the second error is the based on the center coordinate.
                direction_error = self.center - x
                direction_value = direction_pid.get_value(direction_error)
                print("radius: %d, radius_error: %d direction_error: %d, direction_value: %.2f" %
                    (radius, radius_error, direction_error, direction_value))
                # Now produce left and right motor speeds
                self._motor.set_left(0.5 - direction_value)
                self._motor.set_right(0.5 + direction_value)
                time.sleep(0.1)
            else:
                self._motor.stop_all()

if __name__ == '__main__':    
  print("Setting up")
  cv2.namedWindow("output", cv2.WINDOW_NORMAL)

  behavior = ColorTrackingBehavior(Motor())
  behavior.run()
