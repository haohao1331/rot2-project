import serial
import utils
import numpy as np
from gantry import Gantry


utils.print_ports()

ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)
gt = Gantry()

corr_vec = np.array([1 / 32, 1 / 24])

speed = 1000


buffer = ''

# for i in range(100):
#     data = ser.read(1024)
#     print(data)

while True:
    data = ser.read(1024)
    if len(data) > 0:
        # print(str(data))

        data = str(data).replace('b\'', '').replace('\'', '')

        if data.startswith('s') and data.endswith('e') and data.count(',') == 3:
            data = data.replace('e', '').replace('s', '')
            print(data)
            chip_x, chip_y, red_x, red_y = data.split(',')
            # convert to int
            chip_x, chip_y, red_x, red_y = int(chip_x), int(chip_y), int(red_x), int(red_y)

            print(f'chip: {chip_x}, {chip_y} | red: {red_x}, {red_y}')

            vec = np.array([chip_x - red_x, chip_y - red_y]) * corr_vec
            dist = np.linalg.norm(vec)
            vec = vec / dist
            print(dist, vec)

            if dist < 2:
                gt.send(f'G01 X{-vec[0]/2} Y{-vec[1]/2} F{speed}')

        else:
            pass
        