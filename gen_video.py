import cv2
import numpy as np

# Video settings
width, height = 640, 480
fps = 30
duration = 300  # in seconds
frequency = 2  # in Hz

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter("blinking_colors.mp4", fourcc, fps, (width, height))

# Generate frames
num_frames = int(fps * duration)
for frame_num in range(num_frames):
    # Calculate time in seconds
    time_in_seconds = frame_num / fps

    # Calculate color based on time
    color = (0, 255, 0) if (int(time_in_seconds * frequency) % 2 == 0) else (0, 0, 255)

    # Create a frame with the specified color
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = color

    # Write the frame to the video
    video_writer.write(frame)

# Release the VideoWriter
video_writer.release()
