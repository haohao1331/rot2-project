import pandas as pd
import numpy as np
from pathlib import Path
import re
import pickle

def parse_log(log_file : Path, output_file : Path):
    lines = None
    with open(log_file, 'r') as f:
        lines = f.readlines()

    n_blocks = lines.count('\n')
    
    datetime = [None] * n_blocks
    mouse_pos = np.zeros((n_blocks, 2)) - 1
    chip_pos = np.zeros((n_blocks, 2)) - 1
    state = np.zeros(n_blocks) - 1
    distance = np.zeros(n_blocks) - 1
    vector = np.zeros((n_blocks, 2)) + np.nan
    state_switch = np.zeros(n_blocks).astype(bool)
    send_signal = np.zeros((n_blocks, 2)) + np.nan
    tangent_vector = np.zeros((n_blocks, 2)) + np.nan

    block_i = -1
    for i, line in enumerate(lines):
        # print(i)
        # if a line is empty, it indicates the start of a new block
        if line == '\n':
            block_i += 1
            continue
        
        # check if line is a date format
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}', line):
            date = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}', line)[0]
            date = pd.to_datetime(date)
            datetime[block_i] = date
        elif re.match(r'mouse: \d+, \d+ | chip: \d+, \d+', line):
            ints = re.findall(r'\d+', line)
            mouse_pos[block_i] = np.array(ints[:2]).astype(int)
            chip_pos[block_i] = np.array(ints[2:]).astype(int)
        elif re.match(r'state: State.[A-Z]+', line):
            state_str = re.findall(r'e.[A-Z]+', line)[0]
            # print(state_str)
            state[block_i] = 0 if state_str == 'e.MIDDLE' else 1
        elif re.match(r'state switch', line):
            state_switch[block_i] = True
        elif re.match(r'tangent: \[\s*-?1\s*-?1\]', line):
            ints = re.findall(r'-?1', line)
            tangent_vector[block_i] = np.array(ints).astype(int)
        elif re.match(r'\d+.\d+ \[\s*-?\d+.\d*\s*-?\d+.\d*\s*\]', line):
            floats = re.findall(r'-?\d+.\d*', line)
            distance[block_i] = floats[0]
            vector[block_i] = np.array(floats[1:]).astype(float)
        elif re.match(r'send: G01 X-?\d+.\d+ Y-?\d+.\d+ F1000', line):
            floats = re.findall(r'-?\d+.\d+', line)
            send_signal[block_i] = np.array(floats[0:2]).astype(float)
        elif re.match(r"read: b'ok\\r\\n'", line):
            pass
        elif re.match(r'-?\d+,-?\d+,-?\d+,-?\d+', line):
            pass
        else:
            print(f'Unrecognized line: {i, line}')
    
    print(len(datetime), len(mouse_pos), len(chip_pos), len(state), len(distance), len(vector), len(state_switch), len(send_signal), len(tangent_vector))
    print(n_blocks, block_i + 1)
    
    # create pandas dataframe for holding the output
    df = pd.DataFrame({
        'name' : [log_file.name] * n_blocks,
        'datetime': datetime,
        'mouse_pos_x': mouse_pos[:, 0],
        'mouse_pos_y': mouse_pos[:, 1],
        'chip_pos_x': chip_pos[:, 0],
        'chip_pos_y': chip_pos[:, 1],
        'state': state,
        'distance': distance,
        'vector_x': vector[:, 0],
        'vector_y': vector[:, 1],
        'state_switch': state_switch,
        'send_signal_x': send_signal[:, 0],
        'send_signal_y': send_signal[:, 1],
        'tangent_vector_x': tangent_vector[:, 0],
        'tangent_vector_y': tangent_vector[:, 1]
    })

    return df

if __name__ == '__main__':
    log_file_dir = Path(f'/Users/yefan/Desktop/rot2/rot2-project/data/2024-02-09_first_mouse_test_SC23')
    output_dir = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-02-13_first_mouse_test_SC23_analysis')

    dfs = []
    for log_file in sorted(log_file_dir.glob('trial*.txt')):
        # dfs.append(parse_log(log_file, output_dir / f'{log_file.stem}.pkl'))
        parse_log(log_file, output_dir / f'{log_file.stem}.pkl').to_pickle(output_dir / f'{log_file.stem}.pkl')
    # df = pd.concat(dfs)
    # df.to_pickle(output_dir / 'concat_trials.pkl')
    