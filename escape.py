import serial
import utils
import numpy as np
from gantry import Gantry
from enum import Enum
from datetime import datetime
from kalman_filter import KalmanFilter
import matplotlib.pyplot as plt
import pickle
from time import perf_counter
import os

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

# system parameters
control_gantry = True
corr_vec = np.array([483 / 320, 454 / 240]) # convert pixels to milimeter
speed = 3000    # TODO: make this depend on the distance that's required to move
edges = [(279, 220), (41, 223), (37, 23), (276, 25)]
x_max, x_min, y_max, y_min = 270, 45, 210, 30
sub_corner_distance = 30
gantry_history_length = 3
trigger_distance = 120
output_dir = r'C:\git\rot2-project\data\2024-03-17_SC22\trial6_speed3000'

# os.mkdir(output_dir)

chip_kf = KalmanFilter(
    np.array([[100], [100]]), # x and y position
    np.eye(2) * 1000,       # initial variance of the state
    np.array([[1., 0.],     # state transition matrix
              [0., 1.]]), 
    np.array([[1., 0.],     # control matrix
              [0., 1.]]),
    np.array([[1., 0.],     # observation matrix
              [0., 1.]]), 
    np.eye(2) * 1,       # observation noise
    np.eye(2) * 5.0         # process noise
    )

utils.print_ports()
ser = serial.Serial('COM6', baudrate=115200, timeout=0.01)
if control_gantry:
    gt = Gantry()

# system state variables
state = State.MIDDLE
escape_vector = np.array([0, 0])    # for storing escape vector, used when puck is trying to leave a corner
vec_gantry = np.zeros((2))
gantry_cmd_history = np.zeros((gantry_history_length, 2))
prev_mouse_pos = np.zeros((2))  # if camera fails to detect mouse position, previous mouse position is used

mouse_pos_store = []
chip_pos_store = []
chip_pos_raw_store = []
gantry_cmd_store = []

i = 0
try:
    while True:
        data = receive_data(ser)

        if data is None:
            continue
        tic = perf_counter()
        print(f'i: {i}')
        print(datetime.now())

        mouse_x, mouse_y, chip_x, chip_y = data.split(',')
        # convert to int
        chip_x, chip_y, mouse_x, mouse_y = int(chip_x), int(chip_y), int(mouse_x), int(mouse_y)

        print(f'mouse_px: {mouse_x}, {mouse_y} | chip_px: {chip_x}, {chip_y}')

        mouse_pos_mm = np.array([mouse_x, mouse_y]) * corr_vec
        chip_pos_mm = np.array([chip_x, chip_y]) * corr_vec
        chip_pos_raw_store.append(chip_pos_mm)

        print(f'mouse_raw: {mouse_pos_mm[0]}, {mouse_pos_mm[1]} | chip_raw: {chip_pos_mm[0]}, {chip_pos_mm[1]}')

        # update kalman filter
        u = gantry_cmd_history[i % gantry_history_length].reshape(2, 1) * 5

        # chip_kf.predict(u = vec_gantry.reshape(2, 1) * 5)   # using the previous control input
        chip_kf.predict(u = u)    # this will correspond to gantry input from 3 frames ago
        if chip_x != -1:
            chip_kf.update(chip_pos_mm.reshape(2, 1))
        # mouse_kf.predict(u = np.zeros((4, 1)))
        # if mouse_x != -1:
        #     mouse_kf.update(mouse_pos_mm.reshape(2, 1))
            
        if mouse_x == -1:
            mouse_pos_mm = prev_mouse_pos
        
        prev_mouse_pos = mouse_pos_mm

        # print(f'mouse: {mouse_kf.x[0, 0]}, {mouse_kf.x[2, 0]} | chip: {chip_kf.x[0, 0]}, {chip_kf.x[1, 0]}')
        print(f'chip_est: {chip_kf.x[0, 0]}, {chip_kf.x[1, 0]}')

        # mouse_pos_mm = np.array([mouse_kf.x[0, 0], mouse_kf.x[2, 0]])
        chip_pos_mm = np.array([chip_kf.x[0, 0], chip_kf.x[1, 0]])

        mouse_pos_store.append(mouse_pos_mm)
        chip_pos_store.append(chip_pos_mm)

        # print(chip_x, chip_y)

        predicted_chip_pos = chip_pos_mm + np.sum(gantry_cmd_history, axis=0) * 5
        print(f'predicted_chip_pos: {predicted_chip_pos[0]}, {predicted_chip_pos[1]}')
        # print(predicted_chip_pos.shape)
        chip_x, chip_y = predicted_chip_pos[0] / corr_vec[0], predicted_chip_pos[1] / corr_vec[1]

        vec = predicted_chip_pos - mouse_pos_mm    # compute the escape vector first, before using the predicted future chip position
        # an interesting biology question, should the prey's escape strategy depend on it's current position or the predator's predicted future position?
        
        dist = np.linalg.norm(vec)
        print(f'dist: {dist}')
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

                x_edge = np.array([-at_x_max, 0]) * 10
                y_edge = np.array([0, -at_y_max]) * 10

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
        
        vec = vec / (np.linalg.norm(vec) + 0.01)

        print(f'elapsed calculation time: {(perf_counter() - tic) * 1000} ms')
        # actuate gantry
        if control_gantry and dist < trigger_distance:
            vec_gantry = vec * speed / 1000 / 1.3
            gt.send(f'G01 X{-vec_gantry[0]:.2f} Y{-vec_gantry[1]:.2f} F{speed}', wait_for_read=False)  # Note that the coordinate system of the gantry with respect to the camera is flipped
        else:
            vec_gantry = np.zeros((2))
        gantry_cmd_store.append(vec_gantry)
        gantry_cmd_history[i % gantry_history_length] = vec_gantry
        i += 1
        print(f'elapsed time: {(perf_counter() - tic) * 1000} ms')
except KeyboardInterrupt:
    ser.close()
    # gt.close()
    print('interrupted')

    # plot
    mouse_pos_store = np.array(mouse_pos_store)
    chip_pos_store = np.array(chip_pos_store)
    chip_pos_raw_store = np.array(chip_pos_raw_store)
    gantry_cmd_store = np.array(gantry_cmd_store)
    gantry_position = np.cumsum(gantry_cmd_store, axis=0) * 5 + chip_pos_store[0]

    with open(os.path.join(output_dir, 'mouse_pos_store.pkl'), 'wb+') as f:
        pickle.dump(mouse_pos_store, f)
    with open(os.path.join(output_dir, 'chip_pos_store.pkl'), 'wb+') as f:
        pickle.dump(chip_pos_store, f)
    with open(os.path.join(output_dir, 'chip_pos_raw_store.pkl'), 'wb+') as f:
        pickle.dump(chip_pos_raw_store, f)


    plt.plot(chip_pos_store[:, 0], label='chip x est')
    plt.plot(chip_pos_raw_store[:, 0], label='chip x raw')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'chip x.png'))
    plt.close()

    plt.plot(chip_pos_store[:, 1], label='chip y est')
    plt.plot(chip_pos_raw_store[:, 1], label='chip y raw')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'chip y.png'))
    plt.close()

    plt.plot(chip_pos_store[:, 0], chip_pos_store[:, 1], label='chip est')
    plt.plot(chip_pos_raw_store[:, 0], chip_pos_raw_store[:, 1], label='chip raw')
    plt.plot(gantry_position[:, 0], gantry_position[:, 1], label='gantry pos')
    plt.xlim(0, 483)
    plt.ylim(0, 454)
    plt.legend()
    plt.gca().invert_xaxis()
    plt.savefig(os.path.join(output_dir, 'chip pos.png'))
    plt.close()

    plt.plot(mouse_pos_store[:, 0], mouse_pos_store[:, 1], label='mouse pos')
    plt.legend()
    plt.xlim(0, 483)
    plt.ylim(0, 454)
    plt.gca().invert_xaxis()
    plt.savefig(os.path.join(output_dir, 'mouse pos.png'))
    plt.close()

