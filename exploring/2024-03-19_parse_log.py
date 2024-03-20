import pandas as pd
import numpy as np
from pathlib import Path
import re
import pickle

def parse_log(log_file : Path):
    lines = None
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    datetime = []
    mouse_px = []
    mouse_raw, mouse_est = [], []
    chip_px = []
    chip_raw, chip_est = [], []
    state = []
    distance = []
    vec = []
    send_signal = []
    tangent_vector = []
    idx = []
    elapsed_time = []
    elapsed_calc_time = []
    predicted_chip_pos = []

    is_raw = True

    for i, line in enumerate(lines):
        if line.startswith('i: '):
            idx.append(int(re.findall(r'\d+', line)[0]))
            tangent_vector.append(np.array([0, 0]))
            send_signal.append(np.array([0, 0]))
        # check if line is a date format
        elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}', line):
            date = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}', line)[0]
            date = pd.to_datetime(date)
            datetime.append(date)
        elif re.match(r'mouse_px: -?\d+, -?\d+ | chip_px: -?\d+, -?\d+', line):
            ints = re.findall(r'\d+', line)
            mouse_px.append(np.array(ints[:2]).astype(int))
            chip_px.append(np.array(ints[2:]).astype(int))
        elif re.match(r'mouse_raw: -?\d+.\d+, -?\d+.\d+ | chip_raw: -?\d+.\d+, -?\d+.\d+', line):
            floats = re.findall(r'\d+.\d+', line)
            mouse_raw.append(np.array(floats[:2]).astype(float))
            chip_raw.append(np.array(floats[2:]).astype(float))
        elif re.match(r'chip_est: -?\d+.\d+, -?\d+.\d+', line):
            floats = re.findall(r'\d+.\d+', line)
            chip_est.append(np.array(floats).astype(float))
        elif line.startswith('predicted_chip_pos'):
            floats = re.findall(r'-?\d+.\d+', line)
            predicted_chip_pos.append(np.array(floats).astype(float))
        elif line.startswith('vec'):
            ls = [s for s in line.split('[')[-1].split(']')[0].split(' ') if s != '']
            vx, vy = ls[0], ls[1]
            vec.append(np.array([float(vx), float(vy)]))
        elif line.startswith('at edge'):
            pass
        elif re.match(r'state: State.[A-Z]+', line):
            state_str = re.findall(r'e.[A-Z]+', line)[0]
            # print(state_str)
            state.append(0 if state_str == 'e.MIDDLE' else 1)
        elif re.match(r'state switch', line):
            pass
        elif re.match(r'tangent: \[\s*-?1\s*-?1\]', line):
            ints = re.findall(r'-?1', line)
            tangent_vector[-1] = np.array(ints).astype(int)
        elif re.match(r'dist: \d+.\d+', line):
            floats = re.findall(r'-?\d+.\d*', line)
            distance.append(floats[0])
        elif re.match(r'send: G01 X-?\d+.\d+ Y-?\d+.\d+ F\d+', line):
            floats = re.findall(r'-?\d+.\d+', line)
            send_signal[-1] = np.array(floats[0:2]).astype(float)
        elif re.match(r"read: b'ok\\r\\n'", line):
            pass
        elif line.startswith('elapsed time'):
            elapsed_time.append(float(re.findall(r'\d+.\d+', line)[0]))
        elif re.match(r'elapsed calculation time', line):
            elapsed_calc_time.append(float(re.findall(r'\d+.\d+', line)[0]))
        # elif re.match(r'-?\d+,-?\d+,-?\d+,-?\d+', line):
        #     pass
        else:
            print(f'Unrecognized line: {i, line}')
    
    print(len(datetime), len(mouse_px), len(mouse_raw), 
          len(chip_px), len(state), len(distance), len(vec), 
          len(send_signal), len(tangent_vector), len(idx))
    datetime = np.array(datetime)
    mouse_px = np.stack(mouse_px, axis=0)
    elapsed_calc_time, elapsed_time = np.stack(elapsed_calc_time, axis=0), np.stack(elapsed_time, axis=0)
    chip_px = np.stack(chip_px, axis=0)
    chip_raw, chip_est = np.stack(chip_raw, axis=0), np.stack(chip_est, axis=0)
    state = np.array(state)
    distance = np.array(distance)
    vec = np.stack(vec, axis=0)
    send_signal = np.stack(send_signal, axis=0)
    tangent_vector = np.stack(tangent_vector, axis=0)
    idx = np.array(idx)
    predicted_chip_pos = np.stack(predicted_chip_pos, axis=0)
    mouse_raw = np.stack(mouse_raw, axis=0)

    print(type(datetime))
    print(datetime.shape, mouse_px.shape, mouse_raw.shape)

    # create pandas dataframe for holding the output
    df = pd.DataFrame({
        # 'name' : [log_file.name] * n_blocks,
        'datetime': datetime,
        'mouse_px_x': mouse_px[:, 0],
        'mouse_px_y': mouse_px[:, 1],
        'chip_px_x': chip_px[:, 0],
        'chip_px_y': chip_px[:, 1],
        'mouse_raw_x': mouse_raw[:, 0],
        'mouse_raw_y': mouse_raw[:, 1],
        'chip_raw_x': chip_raw[:, 0],
        'chip_raw_y': chip_raw[:, 1],
        'chip_est_x': chip_est[:, 0],
        'chip_est_y': chip_est[:, 1],
        'state': state,
        'distance': distance,
        'vec_x': vec[:, 0],
        'vec_y': vec[:, 1],
        'send_signal_x': send_signal[:, 0],
        'send_signal_y': send_signal[:, 1],
        'tangent_vector_x': tangent_vector[:, 0],
        'tangent_vector_y': tangent_vector[:, 1],
        'predicted_chip_pos_x': predicted_chip_pos[:, 0],
        'predicted_chip_pos_y': predicted_chip_pos[:, 1],
        'elapsed_time': elapsed_time,
        'elapsed_calc_time': elapsed_calc_time,
    })

    return df

if __name__ == '__main__':
    log_file = Path(f'/Users/yefan/Desktop/rot2/rot2-project/data/2024-03-18_SC23/trial2/log.txt')
    output_dir = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-03-19_trajectory_analysis')

    parse_log(log_file).to_pickle(output_dir / f'03-18_SC23_trial2.pkl')
    # df = pd.concat(dfs)
    # df.to_pickle(output_dir / 'concat_trials.pkl')
    