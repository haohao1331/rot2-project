import rpc
import struct

class OpenMV:
    def __init__(self, port='COM6', pixformat_str="sensor.RGB565", framesize_str="sensor.QQVGA") -> None:
        self.port = port
        self.rpc = rpc.rpc_usb_vcp_master(port=port)
        self.pixformat_str = pixformat_str
        self.framesize_str = framesize_str

    def snapshot(self):
        result = self.rpc.call("jpeg_image_snapshot", "%s,%s" % (self.pixformat_str, self.framesize_str))
        # print("%s,%s" % (self.pixformat_str, self.framesize_str))
        if result is None: 
            print("Failed to get image.")
            return
        
        size = struct.unpack("<I", result)[0]
        img = bytearray(size)
        result = self.rpc.call("jpeg_image_read")

        self.rpc.get_bytes(img, 5000)

        return img