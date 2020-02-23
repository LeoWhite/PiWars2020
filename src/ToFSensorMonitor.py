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
from threading import Thread
import VL53L1X

# Defines and constants
JSON_CONFIG_FILE='../config/tb2.json'
UPDATE_TIME_MICROS = 10000
INTER_MEASUREMENT_PERIOD_MILLIS = 20

class ToFMonitorThread(Thread):
    def __init__(self, UDPAddress, name, address):
        Thread.__init__(self)
        self._udp = UDPAddress
        self._name = name
        self._address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=self._address)
        self._tof.open()
        self._tof.set_timing(UPDATE_TIME_MICROS, INTER_MEASUREMENT_PERIOD_MILLIS)


    def run(self):
        message = { "name" : self._name,
                    "distance" : 0,
                    "time" : 0 
                  }
        self._tof.start_ranging(mode=VL53L1X.VL53L1xDistanceMode.SHORT)
        while True:
          message["distance"] = self._tof.get_distance()
          message["time"] = time.time() 
          sock.sendto(json.dumps(message).encode(), self._udp)



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
    sensorMonitor = ToFMonitorThread(udpAddress, address["name"], i2cAddress)
    sensorMonitor.daemon = True
    sensorMonitor.start()
    ToFSensors.append(sensorMonitor)

# Read in the data
running = True

while running:
  time.sleep(10)
  results = []
