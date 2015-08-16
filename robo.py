from serial import Serial

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

serial.write('0P1000T1000\n')
