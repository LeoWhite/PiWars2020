import cv2
import pi_camera_stream
import numpy as np
import time

# start camera
camera = pi_camera_stream.setup_camera()
cv2.namedWindow("output", cv2.WINDOW_NORMAL)
cv2.namedWindow("outputimg", cv2.WINDOW_NORMAL)

# Green
#lowerBound=np.array([60-20,100,50])
#upperBound=np.array([60+20,255,255])

# Red
#lowerBound=np.array([160,100,50])
#upperBound=np.array([179,255,255])


# Blue
lowerBound=np.array([100,100,50])
upperBound=np.array([120,255,255])

# Yello
#lowerBound=np.array([10,100,50])
#upperBound=np.array([20,255,255])


# Whi40
sensitivity = 100
#lowerBound = np.array([0,0,255-sensitivity])
#upperBound = np.array([255,sensitivity,255])

#lowerBound = np.array([0,0,255-sensitivity])
#upperBound = np.array([0,0,255])

        
for frame in pi_camera_stream.start_stream(camera):
  cv2.imshow("output", frame)
  
  # Convert to HSV
  frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
  # Set the masek
  mask=cv2.inRange(frame_hsv,lowerBound,upperBound)
#  cv2.imshow("outputmask", mask)

  kernelOpen=np.ones((5,5))
  kernelClose=np.ones((20,20))

  maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
  maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
  
  maskFinal=maskClose
  conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  cv2.drawContours(frame,conts,-1,(255,0,0),3)

  
  for i in range(len(conts)):
    x,y,w,h=cv2.boundingRect(conts[i])
    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255), 2)
#    cv2.cv.PutText(cv2.cv.fromarray(frame), str(i+1),(x,y+h),font,(0,255,255))



  cv2.imshow("outputimg", frame)

  cv2.waitKey(1)
  #time.sleep(0.1)
  
  
