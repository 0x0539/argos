#!/usr/bin/env python

import sys

class Controller:
  def __init__(self, serial, servos):
    self.serial = serial
    self.servos = servos

  def send(self, command):
    print('Sending: ' + command)
    self.serial.write("#{0}\r".format(command))

  def reset_all(self):
    for name in self.servos:
      self.reset(name)

  def reset(self, name):
    servo = self.servos[name]
    command = servo.reset_cmd()
    self.send(command)

  def move(self, name, position):
    servo = self.servos[name]
    command = servo.move_cmd()
    self.send(command)

  def rotate_pct(self, name, pct):
    servo = self.servos[name]
    command = servo.rotate_pct_cmd(pct)
    self.send(command)

class Servo:
  def __init__(self, index, min_pw, max_pw, neutral_pw=None):
    if min_pw >= max_pw:
      raise ValueError('min_pw=%d, max_pw=%d' % (min_pw, max_pw))
    if min_pw <= 500:
      raise ValueError('min_pw=%d' % min_pw)
    if max_pw > 2500:
      raise ValueError('max_pw=%d' % max_pw)
    self.index = index
    self.min_pw = min_pw
    self.max_pw = max_pw
    self.neutral_pw = neutral_pw if neutral_pw else ((max_pw + min_pw) / 2)
    self.last_pw = None
    if neutral_pw < min_pw or neutral_pw > max_pw:
      raise ValueError('min_pw=%d, neutral_pw=%d, max_pw=%d' % (min_pw, neutral_pw, max_pw))

  def reset_cmd(self):
    return self.move_cmd(self.neutral_pw)

  def move_cmd(self, pw):
    pw = max(min(pw, self.max_pw), self.min_pw)
    self.last_pw = pw
    return '%dP%d' % (self.index, pw)

  def rotate_pct_cmd(self, pct):
    if self.last_pw is None:
      raise Exception('tried to % rotate without initial setting')
    if pct <= -1:
      raise ValueError('pct must be >-1')
    if pct >= 1:
      raise ValueError('pct must be <1')
    rotate_pw = pct * (self.max_pw - self.min_pw)
    pw = self.last_pw + int(rotate_pw)
    return self.move_cmd(pw)
    
