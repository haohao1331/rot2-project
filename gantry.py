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
        # print(self.ser.read())
        time.sleep(2)   # Wait for grbl to initialize
        self.ser.flushInput()
        self.send('G17 G21 G91 G94')    # select XY plane, millimeters, incremental distance mode, feed rate mode to units per minute

    def send(self, msg : str, wait_for_ok=False, wait_for_read=True):
        print(f'send: {msg}')
        self.ser.write(bytes(msg + '\n', self.encoding)) # Send g-code block to grbl
        if wait_for_ok:
            out = []
            ok_str = "b'ok\\r\\n'"
            while True:
                grbl_out = str(self.ser.readline())
                ret = grbl_out.strip()
                print(f'read: {ret}')
                out.append(ret)
                if ret == ok_str:
                    return out[:-1]
        elif wait_for_read:
            grbl_out = str(self.ser.readline())
            ret = grbl_out.strip()
            print(f'read: {ret}')
            return ret
        else:
            return None
    
    def setup(self, max_rate, accel):
        self.send(f'$110={max_rate}')
        self.send(f'$111={max_rate}')
        self.send(f'$120={accel}')
        self.send(f'$121={accel}')

    def close(self):
        self.ser.close()

    def move_x(self, distance, speed):  # TODO: these should be based on differential of current position, but currently it's absolute
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
    
    def get_modal_group(self):
        return self.send('$G', wait_for_ok=True)

    def print_setting(self):
        return self.send('$$', wait_for_ok=True)
    
if __name__ == '__main__':
    gt = Gantry()
    # gt.test()
    # gt.get_modal_group()
    # gt.print_setting()
    # gt.send('?')
    # gt.send('$?')
    # gt.send('$G')
    # gt.move_y(60, 1000)
    gt.move_x(40, 1000)
    # gt.move_x(1, 60)
    gt.close()