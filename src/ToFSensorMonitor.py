#! /usr/bin/python3

# Helper process for monitoring the ToF sensors and exposing
# the details throughout the system.
# Timings and setup taken from https://www.st.com/content/ccc/resource/technical/document/application_note/group1/13/fd/27/76/de/e8/46/4d/DM00566701/files/DM00566701.pdf/jcr:content/translations/en.DM00566701.pdf

# Imports required for this porogram
import json
import signal
import socket
import sys
import time
import VL53L1X

# Defines and constants
JSON_CONFIG_FILE='/home/pi/Programming/PiWars2020/config/tb2.json'
UPDATE_TIME_MICROS = 10000
INTER_MEASUREMENT_PERIOD_MILLIS = 20

# Details on the ToF sensors we are monitoring
ToFSensors = [ ]

# Read in the JSON config file
with open(JSON_CONFIG_FILE) as json_data_file:
    config = json.load(json_data_file)
print(config)

# Setup an exit handler to tidy up if anything goes wrong
def exit_handler(signal, frame):
    global running
    running = False
    for sensor in ToFSensors:
      sensor["tof"].stop_ranging()
    print()
    sys.exit(0)

# Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
signal.signal(signal.SIGINT, exit_handler)

# Create a socket to broadcast the messages on
udpAddress = ( config["ToF"]["udp"]["address"], int(config["ToF"]["udp"]["port"]) )
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Build up a list of the sensors
for address in config['ToF']['sensors']:
    # Convert the string HEX address to a number
    i2cAddress = int(address['i2cAddress'], 16)

    # Initialise the sensor
    tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=i2cAddress)
    tof.open()
    tof.set_timing(UPDATE_TIME_MICROS, INTER_MEASUREMENT_PERIOD_MILLIS)
    tof.start_ranging(mode=VL53L1X.VL53L1xDistanceMode.SHORT)

    ToFSensors.append( { "tof" : tof, "sensor" : address } )

# Read in the data
running = True

while running:
  results = []
  for sensor in ToFSensors:
    results.append(sensor["tof"].get_distance())

    #print("Distance: \t[{}]".format(results[0]))
    message = { "name" : sensor["sensor"]["name"],
                "distance" : results[0],
                "time" : time.time() 
                }
  sock.sendto(json.dumps(message).encode(), udpAddress)
