import rpc
import struct
from time import perf_counter

class OpenMV:
    def __init__(self, port='COM6', pixformat_str="sensor.RGB565", framesize_str="sensor.QQVGA") -> None:
        self.port = port
        self.rpc = rpc.rpc_usb_vcp_master(port=port)
        self.pixformat_str = pixformat_str
        self.framesize_str = framesize_str

    def snapshot(self):
        a = perf_counter()
        result = self.rpc.call("jpeg_image_snapshot", "%s,%s" % (self.pixformat_str, self.framesize_str))
        b = perf_counter()
        print(f'd1: {(b - a)*1000}')
        # print("%s,%s" % (self.pixformat_str, self.framesize_str))
        if result is None: 
            print("Failed to get image.")
            return
        
        size = struct.unpack("<I", result)[0]
        img = bytearray(size)
        c = perf_counter()
        print(f'd2: {(c - b)*1000}')

        result = self.rpc.call("jpeg_image_read")
        d = perf_counter()
        print(f'd3: {(d - c)*1000}')


        self.rpc.get_bytes(img, 5000)
        e = perf_counter()
        print(f'd4: {(e - d)*1000}')

        return img