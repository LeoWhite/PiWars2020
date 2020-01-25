#!/usr/bin/env python

import time
import sys
import signal

import VL53L1X


print("""distance.py

Display the distance read from the sensor.

Uses the "Short Range" timing budget by default.

Press Ctrl+C to exit.

""")


ToFSensors = [ ]
ToFSensorsAddresses = [ 0x20, 0x21, 0x30, 0x31 ]

# Open and start the VL53L1X sensor.
# If you've previously used change-address.py then you
# should use the new i2c address here.
# If you're using a software i2c bus (ie: HyperPixel4) then
# you should `ls /dev/i2c-*` and use the relevant bus number.

for address in ToFSensorsAddresses:
  tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=address)
  tof.open()
  tof.start_ranging(1)

  ToFSensors.append(tof)

running = True

def exit_handler(signal, frame):
    global running
    running = False
    for tof in ToFSensors:
      tof.stop_ranging()
    print()
    sys.exit(0)


# Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
signal.signal(signal.SIGINT, exit_handler)

while running:
  results = []
  for tof in ToFSensors:
    results.append(tof.get_distance())

  print("Distance: \t[{}:{}]\n        \t[{}:{}]".format(results[0], results[1], results[2], results[3]))
  #time.sleep(0.05)
