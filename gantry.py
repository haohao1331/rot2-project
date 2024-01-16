import serial
import time

class Gantry:
    def __init__(self, port='COM5', baudrate=115200, timeout=1) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.encoding = 'UTF-8'
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.ser.write(bytes('\r\n\r\n', 'UTF-8'))
        time.sleep(2)   # Wait for grbl to initialize
        self.ser.flushInput()
        self.send('G17 G20 G90 G94')

    def send(self, msg : str):
        print(f'send: {msg}')
        self.ser.write(bytes(msg + '\n', self.encoding)) # Send g-code block to grbl
        grbl_out = str(self.ser.readline())
        ret = grbl_out.strip()
        print(f'read: {ret}')
        return ret
    
    def setup(self, max_rate, accel):
        self.send(f'$110={max_rate}')
        self.send(f'$111={max_rate}')
        self.send(f'$120={accel}')
        self.send(f'$121={accel}')

    def close(self):
        self.ser.close()

    def move_x(self, distance, speed):
        self.send(f'G01 X{distance} Y0 F{speed}')
    
    def move_y(self, distance, speed):
        self.send(f'G01 X0 Y{distance} F{speed}')
    
    def test(self):
        speed = 60
        distance = 0.5
        self.send(f'G01 X0 Y0 F{speed}')
        self.send(f'G01 X{distance} Y0 F{speed}')
        self.send(f'G01 X0 Y0 F{speed}')
        self.send(f'G01 X0 Y{distance} F{speed}')
        self.send(f'G01 X0 Y0 F{speed}')
        self.send(f'G01 X-{distance} Y0 F{speed}')
        self.send(f'G01 X0 Y0 F{speed}')
        self.send(f'G01 X0 Y-{distance} F{speed}')
        self.send(f'G01 X0 Y0 F{speed}')
    
if __name__ == '__main__':
    gt = Gantry()
    gt.test()
    gt.close()