#! /usr/bin/python3

from guizero import App, Picture, Text

app = App(title="Thunderbird 2", layout="grid")
top_message = Text(app, text="ToF Sensor Output", grid=[1,0])
front_left_message = Text(app, text="0.0", grid=[1,1], align="left")
front_right_message = Text(app, text="0.0", grid=[1,1], align="right")
left_message = Text(app, text="0.0", grid=[0,2], align="right")
tb2 = Picture(app, image="TB2Top.png", grid=[1,2])
left_message = Text(app, text="0.0", grid=[2,2], align="left")
app.display()