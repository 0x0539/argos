#!/usr/bin/env python
import signal
import sys

from time import sleep

from serial import Serial
from servo import Controller
from servo import Servo

from getch import getch
import threading

import freenect
import cv
import frame_convert

class SharedState:
  def __init__(self):
    self.terminated = False

  def terminate(self):
    self.terminated = True

  def is_terminated(self):
    return self.terminated

class KeyboardThread(threading.Thread):
  def run(self):
    print('Press Ctrl-C to quit')
    try:
      while not shared_state.is_terminated():
        key = ord(getch())
        if key == 3:
          shared_state.terminate()
        if key == 97:
          controller.rotate_pct('base', -SHIFT_PCT)
        if key == 101:
          controller.rotate_pct('base', SHIFT_PCT)
        if key == 111:
          controller.rotate_pct('shoulder', SHIFT_PCT)
        if key == 44:
          controller.rotate_pct('shoulder', -SHIFT_PCT)
    except KeyboardInterrupt:
      shared_state.terminate()

shared_state = SharedState()

SHIFT_PCT = .05

serial = Serial(
  port='/dev/ttyUSB0',
  baudrate=9600, 
  bytesize=8, 
  parity='N', 
  stopbits=1, 
  timeout=None, 
  xonxoff=False, 
  rtscts=False, 
  dsrdtr=False
)

servos = {
  'base': Servo(0, 1000, 2000, 1400),
  'shoulder': Servo(4, 1400, 1800, 1600),
}

controller = Controller(serial, servos)
controller.reset_all()

keyboard_thread = KeyboardThread()
keyboard_thread.start()

cv.NamedWindow('Depth')
cv.NamedWindow('RGB')

def display_depth(dev, data, timestamp):
  cv.ShowImage('Depth', frame_convert.pretty_depth_cv(data))
  if cv.WaitKey(10) == 27:
    shared_state.terminate()

def display_rgb(dev, data, timestamp):
  cv.ShowImage('RGB', frame_convert.video_cv(data))
  if cv.WaitKey(10) == 27:
    shared_state.terminate()

def body(*args):
  if shared_state.is_terminated():
    raise freenect.Kill

freenect.runloop(depth=display_depth,
                 video=display_rgb,
                 body=body)

keyboard_thread.join()

serial.close()
