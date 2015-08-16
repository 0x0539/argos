#!/usr/bin/env python
import serial
from serial import tools
from serial.tools import list_ports
import fcntl

def available_ports():
    for tty in list_ports.comports():
        try:
            port = serial.Serial(port=tty[0])
            if port.isOpen():
                try:
                    fcntl.flock(port.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    print 'Port {0} is busy'.format(tty)
                else:
                    yield port
        except serial.SerialException as ex:
            print 'Port {0} is unavailable: {1}'.format(tty, ex)


for port in available_ports():
    print port
