from pyb import UART
import time

class Log():
    def __init__(self) -> None:
        self.log = open(f'log{time.time()}.txt', 'w+')
        self.write('log opened\n')

    def write(self, s):
        self.log.write(s)

    def flush(self):
        self.log.flush()

    def close(self):
        self.log.close()

class Gantry():
    def __init__(self) -> None:
        self.delay = 0 # the delay in ms for waiting gantry response
        self.uart = UART(3, 115200, timeout_char = 1000)
        self.uart.write('\r\n\r\n')
        while self.uart.any() > 0:
            print(self.uart.read())
        # print(self.uart.readline())
        # print(self.uart.any())

    def send(self, msg : str, wait_for_ok=False):
        self.uart.write(bytes(msg + '\n', 'UTF-8')) # Send g-code block to grbl
        # time.sleep_ms(self.delay)
        # while self.uart.any() > 0:
        #     print(self.uart.read())
        # print(self.uart.read())

    def setup(self, max_rate, accel):
        pass

    def close(self):
        self.uart.deinit()

    def move_x(self, distance, speed):  # TODO: these should be based on differential of current position, but currently it's absolute
        pass

    def move_y(self, distance, speed):
        pass

    def test(self):
        self.send('G01 X0 Y-0.5 F60')
        self.send('G01 X0 Y0.5 F60')

if __name__ == '__main__':
    gantry = Gantry()
    gantry.test()
    gantry.close()
