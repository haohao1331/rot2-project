import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import cv2
import pickle
import pandas as pd
from enum import Enum
from datetime import datetime
import time

arena_corners = np.array([(98, 61), (927, 69), (83, 843), (923, 852)], dtype=np.float32)

def overlay(df : pd.DataFrame, video_file : Path, output_file : Path, video_end_time : float = None):
    print(f'video end time: {datetime.fromtimestamp(video_end_time)}')
    assert type(df) == pd.DataFrame, "log file must be a pandas DataFrame"

    # add another column to the dataframe with unix timestamps
    df['unix_timestamp'] = df['datetime'].apply(lambda x: time.mktime(x.timetuple()) + x.microsecond / 1e6)
    print(datetime.fromtimestamp(df['unix_timestamp'].iloc[0]))
    print(df['datetime'].iloc[0])
    n_logs = len(df)

    # print(df.head())

    # loop over every frame of the video
    video = cv2.VideoCapture(str(video_file))
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / frame_rate
    print(f"duration: {duration}, frame count: {frame_count}, frame rate: {frame_rate}")
    print(f"width: {width}, height: {height}")
    unix_timestamp = df['unix_timestamp'].to_numpy()
    offset = 1
    video_start_time = video_end_time - duration + offset

    stretch_factor = (duration + offset) / duration
    unix_timestamp = (unix_timestamp - video_start_time) * stretch_factor + video_start_time

    print(f'video start time: {datetime.fromtimestamp(video_start_time)}')

    mouse_pos_x = (1 - df['mouse_est_x'].to_numpy() / 483) * width
    mouse_pos_y = (1 - df['mouse_est_y'].to_numpy() / 454) * height
    chip_pos_x = (1 - df['chip_est_x'].to_numpy() / 483) * width
    chip_pos_y = (1 - df['chip_est_y'].to_numpy() / 454) * height
    chip_raw_x = (1 - df['chip_raw_x'].to_numpy() / 483) * width
    chip_raw_y = (1 - df['chip_raw_y'].to_numpy() / 454) * height
    mouse_pos = np.concatenate((mouse_pos_x.reshape(-1, 1), mouse_pos_y.reshape(-1, 1)), axis=1).astype(int)
    chip_pos = np.concatenate((chip_pos_x.reshape(-1, 1), chip_pos_y.reshape(-1, 1)), axis=1).astype(int)
    chip_raw_pos = np.concatenate((chip_raw_x.reshape(-1, 1), chip_raw_y.reshape(-1, 1)), axis=1).astype(int)
    print(mouse_pos.shape, chip_pos.shape)
    
    # Calculate the homography matrix
    dst_points = np.array([(0, 0), (width, 0), (0, height), (width, height)], dtype=np.float32)
    H, _ = cv2.findHomography(arena_corners, dst_points)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(str(output_file), fourcc, frame_rate, (width, height))

    frame_i = 0
    while True:
        print(f'\n{frame_i}')
        # cur = time.perf_counter()
        # print(f'{(cur - prev) * 1000} ms')
        # prev = cur
        ret, frame = video.read()
        # if not ret or frame_i >= 18006:
        #     break
        if not ret:
            break
        # get the current time of the frame
        frame_time = video_start_time + frame_i / frame_rate

        # find the nearest unix_timestamp in df
        nearest_i = np.argmin(np.abs(unix_timestamp - frame_time))    # TODO: could optimize
        print(f'nearest_i: {nearest_i}')

        cur_mouse_pos = mouse_pos[nearest_i]
        cur_chip_pos = chip_pos[nearest_i]
        cur_raw_pos = chip_raw_pos[nearest_i]

        frame = cv2.warpPerspective(frame, H, (frame.shape[1], frame.shape[0]))

        if np.abs(unix_timestamp[nearest_i] - frame_time) > 0.2:
            video_writer.write(frame)
            frame_i += 1
            continue
        
        # draw a circle on the frame
        frame = cv2.circle(frame, tuple(cur_mouse_pos), 5, (0, 0, 255), -1)
        frame = cv2.circle(frame, tuple(cur_chip_pos), 5, (0, 255, 0), -1)
        frame = cv2.circle(frame, tuple(cur_raw_pos), 5, (255, 0, 0), -1)
        
        # write the frame to the output file
        video_writer.write(frame)
        frame_i += 1
    
    video.release()
    video_writer.release()
    print("done")

if __name__ == "__main__":
    log_file_dir = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-03-14_fast_speed_analysis')
    log_files = sorted(log_file_dir.glob('*.pkl'))
    dfs = []
    for log_file in log_files:
        dfs.append(pd.read_pickle(log_file))
    df = pd.concat(dfs)
    video_file = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-03-14_SC22/test-03142024162021-0000.avi')
    output_file = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-03-14_fast_speed_analysis') / 'overlay.mp4'
    overlay(df, video_file, output_file, video_end_time=1710460031.2384856)