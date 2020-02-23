#! /usr/bin/python3

# Helper process for monitoring the ToF sensors and exposing
# the details throughout the system.
# Timings and setup taken from https://www.st.com/content/ccc/resource/technical/document/application_note/group1/13/fd/27/76/de/e8/46/4d/DM00566701/files/DM00566701.pdf/jcr:content/translations/en.DM00566701.pdf

# Imports required for this porogram
from guizero import App, Picture, Text
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
          if message["name"] == "front_left":
            self._FLText.value = message["distance"]
          elif message["name"] == "front_right":
            self._FRText.value = message["distance"]
          elif message["name"] == "left":
            self._LText.value = message["distance"]
          elif message["name"] == "right":
            self._RText.value = message["distance"]

# Details on the ToF sensors we are monitoring
ToFSensors = [ ]

# Read in the JSON config file
with open(JSON_CONFIG_FILE) as json_data_file:
    config = json.load(json_data_file)


# Create a socket to broadcast the messages on
udpAddress = ( config["ToF"]["udp"]["address"], int(config["ToF"]["udp"]["port"]) )


# Create the GUI to display the sensor details
app = App(title="Thunderbird 2", layout="grid")
top_message = Text(app, text="ToF Sensor Output", grid=[1,0])
front_left_message = Text(app, text="0.0", grid=[1,1], align="left")
front_right_message = Text(app, text="0.0", grid=[1,1], align="right")
left_message = Text(app, text="0.0", grid=[0,2], align="right")
tb2 = Picture(app, image="TB2Top.png", grid=[1,2])
right_message = Text(app, text="0.0", grid=[2,2], align="left")

# Read in the data
udpMonitor = UDPMonitorThread(udpAddress, front_left_message, front_right_message, left_message, right_message)
udpMonitor.daemon = True
udpMonitor.start()

app.display()
