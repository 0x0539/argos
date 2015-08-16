import serial
import sys
import time


command=sys.argv[1]
print command

print 'Starting Up Serial Monitor'

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)

if not ser.isOpen():
    try:
        ser.open()

    except Exception, e:
        print "error open serial port: " + str(e)
        exit()

if ser.isOpen():

    try:
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output

        ser.write("#{0}\r".format(command))

    except Exception, e:
        print "error communicating...: " + str(e)

else:
    print "cannot open serial port "
