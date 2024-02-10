import serial
import utils
import numpy as np
from gantry import Gantry
from enum import Enum
from datetime import datetime


class State(Enum):
    MIDDLE = 0
    LEAVE_CORNER = 1

state = State.MIDDLE

utils.print_ports()

ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)
gt = Gantry()

corr_vec = np.array([483 / 320, 454 / 240]) # convert pixels to milimeter

speed = 1000    # TODO: make this depend on the distance that's required to move
edges = [(274, 226), (40, 227), (36, 9), (279, 11)]
x_max, x_min, y_max, y_min = 270, 45, 210, 30

sub_corner_distance = 30
escape_vector = np.array([0, 0])

buffer = ''

# for i in range(100):
#     data = ser.read(1024)
#     print(data)

while True:
    data = ser.read(1024)
    if len(data) == 0:
        # print(str(data))
        continue

    data = str(data).replace('b\'', '').replace('\'', '')

    if not (data.startswith('s') and data.endswith('e') and data.count(',') == 3):  # data not formatted properly, just omit this batch
        continue


    print('')
    print(datetime.now())
    data = data.replace('e', '').replace('s', '')
    print(data)
    mouse_x, mouse_y, chip_x, chip_y = data.split(',')
    # convert to int
    chip_x, chip_y, mouse_x, mouse_y = int(chip_x), int(chip_y), int(mouse_x), int(mouse_y)

    print(f'mouse: {mouse_x}, {mouse_y} | chip: {chip_x}, {chip_y}')

    diff_vec = np.array([chip_x - mouse_x, chip_y - mouse_y]) * corr_vec
    vec = diff_vec.copy()
    print(f'state: {state}')

    if state == State.MIDDLE:
        corner = (chip_x >= x_max or chip_x <= x_min) and (chip_y >= y_max or chip_y <= y_min)
        if not corner:
            # edge constraints
            if chip_x >= x_max:
                vec[0] = min(0, vec[0])
            elif chip_x <= x_min:
                vec[0] = max(0, vec[0])
            if chip_y >= y_max:
                vec[1] = min(0, vec[1])
            elif chip_y <= y_min:
                vec[1] = max(0, vec[1])
        else:
            state = State.LEAVE_CORNER  # switch state
            print('state switch to LEAVE_CORNER')

            at_x_max = int(chip_x >= x_max) * 2 - 1
            at_y_max = int(chip_y >= y_max) * 2 - 1

            # assume we are dealing with top left corner
            tangent = np.array([at_x_max, -at_y_max])
            print(f'tangent: {tangent}')

            x_edge = np.array([-at_x_max, 0])
            y_edge = np.array([0, -at_y_max])

            # project onto tangent, and then project onto edge
            tangent_proj = np.dot(vec, tangent)

            if tangent_proj >= 0:
                escape_vector = y_edge
            else:
                escape_vector = x_edge

            vec = escape_vector

    elif state == State.LEAVE_CORNER:
        sub_corner = False
        if (chip_x >= x_max - sub_corner_distance) and (chip_y >= y_max - sub_corner_distance):
            sub_corner = True
        elif (chip_x <= x_min + sub_corner_distance) and (chip_y >= y_max - sub_corner_distance):
            sub_corner = True
        elif (chip_x <= x_min + sub_corner_distance) and (chip_y <= y_min + sub_corner_distance):
            sub_corner = True
        elif (chip_x >= x_max - sub_corner_distance) and (chip_y <= y_min + sub_corner_distance):
            sub_corner = True
    
        vec = escape_vector

        if not sub_corner:
            state = State.MIDDLE
            print('state switch to MIDDLE')
    
    dist = np.linalg.norm(vec) + 0.01
    vec = vec / dist
    print(dist, vec)

    if dist < 70:
        gt.send(f'G01 X{-vec[0]} Y{-vec[1]} F{speed}')  # Note that the coordinate system of the gantry with respect to the camera is flipped