import serial
import utils
import numpy as np
from gantry import Gantry
from enum import Enum
from datetime import datetime
from kalman_filter import KalmanFilter
import matplotlib.pyplot as plt

class State(Enum):
    MIDDLE = 0
    LEAVE_CORNER = 1

def receive_data(ser):
    data = ser.read(1024)
    if len(data) == 0:
        return None

    data = str(data).replace('b\'', '').replace('\'', '')

    if not (data.startswith('s') and data.endswith('e') and data.count(',') == 3):  # data not formatted properly, just omit this batch
        return None

    data = data.replace('e', '').replace('s', '')
    # print(data)
    return data

state = State.MIDDLE
control_gantry = True

utils.print_ports()

ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)
if control_gantry:
    gt = Gantry()

corr_vec = np.array([483 / 320, 454 / 240]) # convert pixels to milimeter

speed = 1500    # TODO: make this depend on the distance that's required to move
edges = [(279, 220), (41, 223), (37, 23), (276, 25)]
x_max, x_min, y_max, y_min = 270, 45, 210, 30

sub_corner_distance = 30
escape_vector = np.array([0, 0])

chip_kf = KalmanFilter(
    np.array([[100], [100]]), # x and y position
    np.eye(2) * 1000, 
    np.array([[1., 0.], 
              [0., 1.]]), 
    np.array([[1., 0.],
              [0., 1.]]),
    np.array([[1., 0.],
              [0., 1.]]), 
    np.eye(2) * 0.01, 
    np.eye(2) * 5.0
    )
# mouse_kf = KalmanFilter(
#     np.array([[0], [0], [0], [0]]), # x, x_vel, y, y_vel
#     np.eye(4) * 1000, 
#     np.array([[1., 1., 0., 0.], 
#               [0., 1., 0., 0.],
#               [0., 0., 1., 1.],
#               [0., 0., 0., 1.]]), 
#     np.zeros((4, 4)),
#     np.array([[1., 0., 0., 0.],
#               [0., 0., 1., 0.]]), 
#     np.eye(4) * 0.01, 
#     np.eye(2) * 5.0
#     )

mouse_pos_store = []
chip_pos_store = []
chip_pos_raw_store = []
vec_gantry = np.zeros((2))


i = 0
try:
    while True:
        data = receive_data(ser)

        if data is None:
            continue
        print(f'i: {i}')
        print(datetime.now())

        mouse_x, mouse_y, chip_x, chip_y = data.split(',')
        # convert to int
        chip_x, chip_y, mouse_x, mouse_y = int(chip_x), int(chip_y), int(mouse_x), int(mouse_y)

        print(f'mouse_px: {mouse_x}, {mouse_y} | chip_px: {chip_x}, {chip_y}')

        mouse_pos_mm = np.array([mouse_x, mouse_y]) * corr_vec
        chip_pos_mm = np.array([chip_x, chip_y]) * corr_vec
        chip_pos_raw_store.append(chip_pos_mm)

        print(f'mouse: {mouse_pos_mm[0]}, {mouse_pos_mm[1]} | chip: {chip_pos_mm[0]}, {chip_pos_mm[1]}')

        # update kalman filter
        chip_kf.predict(u = vec_gantry.reshape(2, 1) * 5)
        if chip_x != -1:
            chip_kf.update(chip_pos_mm.reshape(2, 1))
        # mouse_kf.predict(u = np.zeros((4, 1)))
        # if mouse_x != -1:
        #     mouse_kf.update(mouse_pos_mm.reshape(2, 1))

        # print(f'mouse: {mouse_kf.x[0, 0]}, {mouse_kf.x[2, 0]} | chip: {chip_kf.x[0, 0]}, {chip_kf.x[1, 0]}')
        print(f'mouse: {mouse_pos_mm[0]}, {mouse_pos_mm[1]} | chip: {chip_kf.x[0, 0]}, {chip_kf.x[1, 0]}')

        # mouse_pos_mm = np.array([mouse_kf.x[0, 0], mouse_kf.x[2, 0]])
        chip_pos_mm = np.array([chip_kf.x[0, 0], chip_kf.x[1, 0]])

        mouse_pos_store.append(mouse_pos_mm)
        chip_pos_store.append(chip_pos_mm)

        chip_x, chip_y = chip_pos_mm[0] / corr_vec[0], chip_pos_mm[1] / corr_vec[1]
        # print(chip_x, chip_y)

        vec = chip_pos_mm - mouse_pos_mm
        print(f'vec: {vec}')

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
                
                print(f'at edge, vec: {vec}')
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
            sub_corner = (chip_x >= x_max - sub_corner_distance) and (chip_y >= y_max - sub_corner_distance) \
                        or (chip_x <= x_min + sub_corner_distance) and (chip_y >= y_max - sub_corner_distance) \
                        or (chip_x <= x_min + sub_corner_distance) and (chip_y <= y_min + sub_corner_distance) \
                        or (chip_x >= x_max - sub_corner_distance) and (chip_y <= y_min + sub_corner_distance)
        
            vec = escape_vector

            if not sub_corner:
                state = State.MIDDLE
                print('state switch to MIDDLE')
        
        dist = np.linalg.norm(vec) + 0.01
        vec = vec / dist
        print(f'dist: {dist}')


        # actuate gantry
        if control_gantry and dist < 100:
            vec_gantry = vec * speed / 1000
            gt.send(f'G01 X{-vec_gantry[0]} Y{-vec_gantry[1]} F{speed}')  # Note that the coordinate system of the gantry with respect to the camera is flipped
        else:
            vec_gantry = np.zeros((2))
        i += 1
except KeyboardInterrupt:
    ser.close()
    # gt.close()
    print('interrupted')

    # plot
    mouse_pos_store = np.array(mouse_pos_store)
    chip_pos_store = np.array(chip_pos_store)
    chip_pos_raw_store = np.array(chip_pos_raw_store)


    plt.plot(chip_pos_store[:, 0], label='chip x est')
    plt.plot(chip_pos_raw_store[:, 0], label='chip x raw')
    plt.legend()
    plt.savefig('chip x.png')
    plt.close()

    plt.plot(chip_pos_store[:, 1], label='chip y est')
    plt.plot(chip_pos_raw_store[:, 1], label='chip y raw')
    plt.legend()
    plt.savefig('chip y.png')
    plt.close()

    plt.plot(chip_pos_store[:, 0], chip_pos_store[:, 1], label='chip est')
    plt.plot(chip_pos_raw_store[:, 0], chip_pos_raw_store[:, 1], label='chip raw')
    plt.xlim(0, 483)
    plt.ylim(0, 454)
    plt.legend()
    plt.savefig('chip pos.png')
    plt.close()

    plt.plot(mouse_pos_store[:, 0], mouse_pos_store[:, 1], label='mouse pos')
    plt.legend()
    plt.savefig('mouse pos.png')
    plt.close()

