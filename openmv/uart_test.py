from pyb import UART
import time

uart = UART(3, 115200, timeout_char = 1000)
#uart = UART(3, 115200)
uart.write('\r\n\r\n')

print(uart.readline())

#for i in range(uart.any()):
    #print(uart.readchar())
#print(uart.read())

uart.write(bytes('G01 X0 Y-0.5 F60' + '\n', 'UTF-8'))
#time.sleep_ms(50)
grbl_out = str(uart.read())
print(grbl_out)
#while uart.any() == 0:
    #continue
print(uart.any())
print(uart.readline())

uart.write(bytes('G01 X0 Y0.5 F60' + '\n', 'UTF-8'))
#time.sleep_ms(50)
print(uart.readline())

#uart.close()

#for i in range(av):
    #print(uart.read())

#print(ret)

#time.sleep(2)   # Wait for grbl to initialize

#ret = uart.read()
#print(ret)


#uart.write('$$') # Send g-code block to grbl
#av = uart.any()
#print(uart.any())
#for i in range(av):
    #print(uart.read())

#ret = True

#while ret != None:
    #ret = uart.read()
    #print(ret)
