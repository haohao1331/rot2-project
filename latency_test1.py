# imporved version of the latency test, where only red/green is sent
from time import perf_counter
from gantry import Gantry
import serial


speed = 120

gt = Gantry()
ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)

now = perf_counter()
a, b, c, d = 0, 0, 0, 0

prev_direction = None

while True:
    now = perf_counter()
    
    print(f'\nwait: {(now - d)*1000}')

    data = ser.read(1024)
    if len(data) <= 0:
        continue

    data = str(data)
    print(data)
    if 'e' not in data:
        continue
    if data.startswith('e'):
        data = data[1:]
    direction = data.split('e')[0].split(' : ')[1]

    if direction != prev_direction:
        gt.move_y(int(direction) / 2, speed)
        prev_direction = direction
    d = perf_counter()
    print(f'move: {(d - now)*1000}')