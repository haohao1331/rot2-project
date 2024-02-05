from pyb import UART
import time
import pyb

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

class VCP():
    def __init__(self, log) -> None:
        #for i in range(100):
            #try:
                #self.vcp = pyb.USB_VCP(i)
                #assert self.vcp.isconnected()
                #log.write(f'vcp {i} created\n')
                #break
            #except:
                #log.write(f'vcp {i} failed\n')
        self.vcp = pyb.USB_VCP(0)
        self.log = log

        self.log.write('vcp created\n')
        # assert self.vcp.isconnected() # for some reason this simply doesn't work without the IDE
        # log.write('vcp connected\n')

    def write(self, buf):
        self.vcp.write(buf)
        self.log.write(f'wrote {buf}\n')
        self.log.flush()

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

    def close(self):
        self.uart.deinit()

    def test(self):
        self.send('G01 X0 Y-0.5 F60')
        self.send('G01 X0 Y0.5 F60')

def blink_led(a):
    led = pyb.LED(a)
    led.on()
    pyb.delay(200)
    led.off()
    return

if __name__ == '__main__':
    gantry = Gantry()
    gantry.test()
    gantry.close()
