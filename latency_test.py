import io
from pathlib import Path
from time import perf_counter
from PIL import Image
import time
import numpy as np
from gantry import Gantry
from openmv import OpenMV
import cv2
from red_or_green import analyze_image_for_red_green


output_dir = Path(r'C:\git\rot2-project\data\2024-01-15_camera_pics1')
delta = 0.1
speed = 60
cur_pos = 0

gt = Gantry()
omv = OpenMV()

now = perf_counter()
prev = now

while(True):
    now = perf_counter()
    print(f'\n{(now - prev)*1000:.0f}')
    prev = now

    img = omv.snapshot()
    if img is None:
        continue

    img = cv2.imdecode(np.frombuffer(img, dtype=np.uint8), -1)

    # print(type(img))

    dominant_color, red_count, green_count, mask_red, mask_green = analyze_image_for_red_green(img)

    print(f'{dominant_color}')

    cur_pos += delta if dominant_color == 'red' else -delta
    gt.move_y(cur_pos, speed)

    # if dominant_color == 'red':
    #     gt.move_x(distance, speed)
    # else:
    #     gt.move_x(-distance, speed)

    # img.save(output_dir / f'{now}.jpg')
    # np.save(output_dir / f'test.jpg', img)
    # break