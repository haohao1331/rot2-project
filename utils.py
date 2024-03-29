# Description: Utility functions for working with serial ports and video files
from pathlib import Path
import cv2

def print_ports():
    import serial.tools.list_ports
    # Get a list of available serial ports
    ports = serial.tools.list_ports.comports()

    # Iterate through each port and check for signal
    for port in ports:
        try:
            # Open the port
            ser = serial.Serial(port.device)
            
            # Check if there is a signal
            if ser.readable():
                print(f"Port {port.device} has a signal")
            else:
                print(f"Port {port.device} does not have a signal")
            
            # Close the port
            ser.close()
        except serial.SerialException:
            print(f"Error opening port {port.device}")

def concatenate_avi_files(input_files, output_file):
    '''
    input_files: list of Path objects
    output_file: Path object
    this function takes a list of videos and concatenates them
    '''
    # Create a VideoWriter object to write the output file
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = get_frame_rate(input_files[0])  # Adjust the frame rate as needed
    frame_size = get_frame_size(input_files[0])
    print(fps, frame_size)
    output_video = cv2.VideoWriter(str(output_file), fourcc, fps, frame_size)

    # Iterate through input files and write frames to the output video
    for file in input_files:
        print(file)
        # Open the input video file
        cap = cv2.VideoCapture(str(file))

        # Read and write frames until the end of the video
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            output_video.write(frame)

        # Release the VideoCapture object
        cap.release()

    # Release the VideoWriter object
    output_video.release()

    print(f"Concatenation complete. Output file saved as '{output_file}'.")

def get_frame_rate(video_path):
    # Open the video file
    cap = cv2.VideoCapture(str(video_path))

    # Get the frame rate of the video
    frame_rate = cap.get(cv2.CAP_PROP_FPS)

    # Release the VideoCapture object
    cap.release()

    return frame_rate

def get_frame_size(video_path):
    # Open the video file
    cap = cv2.VideoCapture(str(video_path))

    # Get the frame width and height of the video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Release the VideoCapture object
    cap.release()

    return frame_width, frame_height


if __name__ == "__main__":
    path = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-02-09_first_mouse_test_SC23')
    # path = Path('/Users/yefan/Desktop/rot2/rot2-project/data/2024-02-09_first_mouse_test_SC23/mouse-02092024150334-0000.avi')
    # print([get_frame_rate(str(a)) for a in sorted(path.glob('*.avi'))])
    # print([get_frame_size(str(a)) for a in sorted(path.glob('*.avi'))])
    concatenate_avi_files(sorted(path.glob('*.avi')), path / 'concatenated.mp4')