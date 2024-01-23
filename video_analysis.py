import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
from red_or_green import analyze_image_for_red_green

def analyze_video(vid_path : Path, txt_output : Path):
    # Open the video file
    cap = cv2.VideoCapture(vid_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the number of frames in the video
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    y_loc = np.zeros(num_frames)
    is_red = np.zeros(num_frames)

    # Loop through all the frames
    for i in range(num_frames):
        # Read the frame
        success, frame = cap.read()

        # Check if frame read successfully
        if not success:
            print("Error: Could not read frame from video.")
            return

        cx, cy = get_centre_dot_location(frame)
        y_loc[i] = cy
        dominant_color, red_count, green_count, mask_red, mask_green = analyze_image_for_red_green(frame[600:, 0:400, :])
        is_red[i] = 1 if dominant_color == 'red' else 0
        print(f'{i} - {cy} - {dominant_color} - {red_count} - {green_count}')

    np.save(f'/Users/yefan/Desktop/rot2/rot2-project/temp/y_loc.npy', np.array(y_loc))
    plt.plot(y_loc)
    plt.show()
    np.save(f'/Users/yefan/Desktop/rot2/rot2-project/temp/is_red.npy', np.array(is_red))
    plt.plot(is_red)
    plt.show()

    # Release the video capture object
    cap.release()

def get_centre_dot_location(snapshot) -> tuple:
    max_area = 2000
    min_area = 200
    
    if type(snapshot) in [Path, str]:
        img = cv2.imread(snapshot)
    else:
        img = snapshot
    img_size = img.shape
    # print(img_size)
    img = img[100:img_size[0]//2 + 200, 100:img_size[1]//2, :]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 127, 255, 0)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # contour_img = cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

    for contour in contours:
        # Calculate contour area
        area = cv2.contourArea(contour)
        # print(area)

        # Draw contour if its area is below the specified max area
        if min_area < area < max_area:
            cv2.drawContours(img, contour, -1, (0, 255, 0), 3)
            M = cv2.moments(contour)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # print(f'cx: {cx}, cy: {cy}')
            return cx, cy
    return -1, -1


    # plt.imshow(img)
    # plt.show()

def extract_image_from_movie(movie_path : Path, output_image_path, time_in_seconds):
    # Open the video file
    cap = cv2.VideoCapture(movie_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Set the time position in seconds
    cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds*1000)

    # Read one frame
    success, image = cap.read()

    if success:
        # Save the frame as an image file
        cv2.imwrite(output_image_path, image)
        print(f"Image successfully saved to {output_image_path}")
    else:
        print("Error: Could not read frame from video.")

    # Release the video capture object
    cap.release()

if __name__ == '__main__':
    vid_path = r'/Users/yefan/Desktop/rot2/rot2-project/data/2024-01-19_video_analysis/test1-01152024155717-0000.avi'
    # snapshot_path = r'C:\git\rot2-project\data\2024-01-15_video_data\snapshot.jpg'
    # # extract_image_from_movie(vid_path, snapshot_path, 21)
    # # get_centre_dot_location(snapshot_path)
    analyze_video(vid_path, None)

    # loc_path = Path('/Users/yefan/Desktop/rot2/rot2-project/temp/temp.npy')
    # img = cv2.imread('/Users/yefan/Desktop/rot2/rot2-project/data/2024-01-19_video_analysis/snapshot.jpg')
    # img = img[600:, 0:400, :]
    # # plt.imshow(img)
    # # plt.show()
    # # exit()
    # dominant_color, red_count, green_count, mask_red, mask_green = analyze_image_for_red_green(img)
    # print(dominant_color, red_count, green_count)


