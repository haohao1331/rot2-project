

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

def send_msg(ser, msg):
    print('Sending: ' + msg)
    ser.write(bytes(msg + '\n', 'UTF-8')) # Send g-code block to grbl
    grbl_out = str(ser.readline())
    print(' : ' + grbl_out.strip())

def setup(ser, max_rate, accel):
    send_msg(ser, '$110=' + str(max_rate))
    send_msg(ser, '$111=' + str(max_rate))
    send_msg(ser, '$120=' + str(accel))
    send_msg(ser, '$121=' + str(accel))

def test_gantry():
    import serial
    import time
    import previous.trajectory as tj
    import numpy as np

    # Open the port
    ser = serial.Serial('COM5', 115200, timeout=1)

    # Wake up grbl
    ser.write(bytes('\r\n\r\n', 'UTF-8'))
    time.sleep(2)   # Wait for grbl to initialize
    ser.flushInput()  # Flush startup text in serial input

    distance = 0.5
    speed = 60

    # setup(ser, 8000, 750)

    # Lissajous
    g = []
    g.append('G17 G20 G90 G94') # inches
    g.append(f'G01 X0 Y0 F{speed}')
    g.append(f'G01 X{distance} Y0 F{speed}')
    g.append(f'G01 X0 Y0 F{speed}')
    g.append(f'G01 X0 Y{distance} F{speed}')
    g.append(f'G01 X0 Y0 F{speed}')
    g.append(f'G01 X-{distance} Y0 F{speed}')
    g.append(f'G01 X0 Y0 F{speed}')
    g.append(f'G01 X0 Y-{distance} F{speed}')
    g.append(f'G01 X0 Y0 F{speed}')


    for msg in g:
        print('Sending: ' + msg)
        ser.write(bytes(msg + '\n', 'UTF-8')) # Send g-code block to grbl
        grbl_out = str(ser.readline())
        print(' : ' + grbl_out.strip())
    
    ser.close()

def test_grbl():
    import serial
    import time
    import previous.trajectory as tj
    import numpy as np

    # Open the port
    ser = serial.Serial('COM5', 115200, timeout=1)

    # Wake up grbl
    ser.write(bytes('\r\n\r\n', 'UTF-8'))
    time.sleep(2)   # Wait for grbl to initialize
    ser.flushInput()  # Flush startup text in serial input

    send_msg(ser, 'G17 G20 G90 G94') # inches
    send_msg(ser, '$$')
    for i in range(10):
        grbl_out = str(ser.readline())
        print(' : ' + grbl_out.strip())

    # send_msg(ser, '$#')
    # send_msg(ser, '?')

    ser.close()

if __name__ == "__main__":
    test_gantry()
    # test_grbl()