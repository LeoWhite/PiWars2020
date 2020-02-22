#! /usr/bin/python3

# Helper process for monitoring the ToF sensors and exposing
# the details throughout the system.
# Timings and setup taken from https://www.st.com/content/ccc/resource/technical/document/application_note/group1/13/fd/27/76/de/e8/46/4d/DM00566701/files/DM00566701.pdf/jcr:content/translations/en.DM00566701.pdf

# Imports required for this porogram
import json
import socket
import sys

# Defines and constants
JSON_CONFIG_FILE='/home/pi/Programming/PiWars2020/config/tb2.json'

# Details on the ToF sensors we are monitoring
ToFSensors = [ ]

# Create the 
# Read in the JSON config file
with open(JSON_CONFIG_FILE) as json_data_file:
    config = json.load(json_data_file)
print(config)


# Create a socket to broadcast the messages on
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpAddress = ( config["ToF"]["udp"]["address"], int(config["ToF"]["udp"]["port"]) )
sock.bind(udpAddress)

# Read in the data
running = True

while running:
  results = []
  data, addr = sock.recvfrom(1024)

  message = json.loads(data)
  print(message["name"], message["distance"], message["time"])
  #time.sleep(0.05)
