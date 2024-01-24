import serial
import utils


utils.print_ports()

ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)


while True:
    data = ser.read(1024)
    if len(data) > 0:
        print(data)