#!/usr/bin/env python
from __future__ import with_statement

import signal
import sys

from time import sleep

from serial import Serial
from servo import Controller
from servo import Servo

from getch import getch
import threading

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

while not shared_state.is_terminated():
  sleep(1)

keyboard_thread.join()
serial.close()
