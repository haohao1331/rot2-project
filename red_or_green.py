import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import shutil

def analyze_image_for_red_green(image):
    # Read the image
    # image = cv2.imread(str(image_path))

    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define range for red color in HSV
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Define range for green color in HSV
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # Create masks for red and green
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Combine red masks
    mask_red = mask_red1 + mask_red2

    # Calculate the amount of red and green pixels
    red_count = np.sum(mask_red != 0)
    green_count = np.sum(mask_green != 0)

    # Determine dominant color
    if green_count - red_count > 800:
        dominant_color = "green"
    else:
        dominant_color = "red"
    
    return dominant_color, red_count, green_count, mask_red, mask_green

def generate_square_wave(input_dir : Path, output_dir : Path): 
    # Get all the images in the input directory
    images = sorted(input_dir.glob('*.jpg'))

    # Create a list to store the dominant color of each image
    dominant_colors = []

    # Loop through all the images
    for image in images:
        # Analyze the image for red and green
        dominant_color, red_count, green_count, mask_red, mask_green = analyze_image_for_red_green(image)
        print(f'{image.name} - {dominant_color} - {red_count} - {green_count}')

        # Append the dominant color to the list
        dominant_colors.append(dominant_color)

        # save the masks
        cv2.imwrite(str(output_dir / f'{image.name}_mask_red.jpg'), mask_red)
        cv2.imwrite(str(output_dir / f'{image.name}_mask_green.jpg'), mask_green)

        # Save the image with the dominant color
        shutil.copy(image, output_dir / f'{image.name}_{dominant_color}.jpg')

    exit()

    # Create a list to store the square wave
    square_wave = []

    # Loop through all the dominant colors
    for i in range(len(dominant_colors)):
        # If the dominant color is red, append a 1 to the square wave
        if dominant_colors[i] == "red":
            square_wave.append(1)
        # If the dominant color is green, append a 0 to the square wave
        elif dominant_colors[i] == "green":
            square_wave.append(0)
        # If the dominant color is none, append the previous value to the square wave
        else:
            square_wave.append(square_wave[i-1])

    return square_wave

def traverse_dir_and_rename(input_dir : Path):
    # Get all the images in the input directory
    images = sorted(input_dir.glob('*.jpg'))

    # Loop through all the images
    for img in images:
        # Rename the image
        original = float(img.name.replace('.jpg', ''))
        img.rename(input_dir / f'{original:3f}.jpg')


if __name__ == "__main__":
    path = Path(r'C:\git\rot2-project\data\2024-01-15_camera_pics1')
    output_path = Path(r'C:\git\rot2-project\data\2024-01-15_color_labels')
    traverse_dir_and_rename(path)
    result = generate_square_wave(path, output_path)
    # print(result)