#! /usr/bin/python3

from guizero import App, Picture, Text
from threading import Thread
from time import sleep

class UpdateThread(Thread):

    def __init__(self, FLMessage):
        Thread.__init__(self)
        self.FLMessage = FLMessage
        self.count=0

    def run(self):
        while True:
            self.count = self.count + 1
            self.FLMessage.value = str(self.count)
            sleep(1.0)

app = App(title="Thunderbird 2", layout="grid")
top_message = Text(app, text="ToF Sensor Output", grid=[1,0])
front_left_message = Text(app, text="0.0", grid=[1,1], align="left")
front_right_message = Text(app, text="0.0", grid=[1,1], align="right")
left_message = Text(app, text="0.0", grid=[0,2], align="right")
tb2 = Picture(app, image="TB2Top.png", grid=[1,2])
left_message = Text(app, text="0.0", grid=[2,2], align="left")

updater = UpdateThread(front_left_message)
updater.daemon = True
updater.start()

app.display()
