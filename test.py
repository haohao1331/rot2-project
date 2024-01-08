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
