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
import cv2
import frame_convert2
import numpy as np

SERVO = False
KINECT = True
SHIFT_PCT = .05

class SharedState:
  def __init__(self):
    self.terminated = False

  def terminate(self):
    self.terminated = True

  def is_terminated(self):
    return self.terminated

class KeyboardThread(threading.Thread):
  def __init__(self, shared_state, controller):
    super(KeyboardThread, self).__init__()
    self._shared_state = shared_state
    self._controller = controller

  def run(self):
    print('Press Ctrl-C to quit')
    try:
      while not self._shared_state.is_terminated():
        key = ord(getch())
        if key == 3:
          self._shared_state.terminate()
        if key == 97:
          self._controller.rotate_pct('base', -SHIFT_PCT)
        if key == 101:
          self._controller.rotate_pct('base', SHIFT_PCT)
        if key == 111:
          self._controller.rotate_pct('shoulder', SHIFT_PCT)
        if key == 44:
          self._controller.rotate_pct('shoulder', -SHIFT_PCT)
    except KeyboardInterrupt:
      self._shared_state.terminate()

def main():
  shared_state = SharedState()

  if SERVO:
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
  else:
    controller=None

  keyboard_thread = KeyboardThread(shared_state, controller)
  keyboard_thread.start()

  cv2.namedWindow('Depth')
  cv2.namedWindow('RGB')

  face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
  eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml')

  def display_depth(dev, data, timestamp):
    cv2.imshow('Depth', frame_convert2.pretty_depth_cv(data))
    if cv2.waitKey(10) == 27:
      shared_state.terminate()

  def display_rgb(dev, data, timestamp):
    img = np.array(frame_convert2.video_cv(data))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    cv2.putText(img, '%d faces' % len(faces), (50,50), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,255))
    for (x,y,w,h) in faces:
      cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
      roi_gray = gray[y:y+h, x:x+w]
      roi_color = img[y:y+h, x:x+w]
      eyes = eye_cascade.detectMultiScale(roi_gray)
      for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
    cv2.imshow('RGB', img)
    if cv2.waitKey(10) == 27:
      shared_state.terminate()

  def body(*args):
    if shared_state.is_terminated():
      raise freenect.Kill

  freenect.runloop(
    depth=display_depth,
    video=display_rgb,
    body=body
  )

  keyboard_thread.join()

  if SERVO:
    serial.close()

if __name__ == '__main__':
  main()
