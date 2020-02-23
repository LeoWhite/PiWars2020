#! /usr/bin/python3

# Helper process for monitoring the ToF sensors and exposing
# the details throughout the system.
# Timings and setup taken from https://www.st.com/content/ccc/resource/technical/document/application_note/group1/13/fd/27/76/de/e8/46/4d/DM00566701/files/DM00566701.pdf/jcr:content/translations/en.DM00566701.pdf

# Imports required for this porogram
import json
import socket
import sys
from threading import Thread
import time

# Defines and constants
JSON_CONFIG_FILE='/home/pi/Programming/PiWars2020/config/tb2.json'

# Thread that monitors for UDP packets in the background
class UDPMonitorThread(Thread):
    def __init__(self, UDPAddress, FLText, FRText, LText, RText):
        Thread.__init__(self)
        self._FLText = FLText
        self._FRText = FRText
        self._LText = LText
        self._RText = RText
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(UDPAddress)

    def run(self):
        while True:
          data, addr = self.socket.recvfrom(1024)

          message = json.loads(data)
          print(message["name"], message["distance"], message["time"])

# Details on the ToF sensors we are monitoring
ToFSensors = [ ]

# Read in the JSON config file
with open(JSON_CONFIG_FILE) as json_data_file:
    config = json.load(json_data_file)


# Create a socket to broadcast the messages on
udpAddress = ( config["ToF"]["udp"]["address"], int(config["ToF"]["udp"]["port"]) )

# Read in the data
udpMonitor = UDPMonitorThread(udpAddress, 0, 0, 0, 0)
udpMonitor.daemon = True
udpMonitor.start()

running = True

while running:
  time.sleep(5)
