import sensor
import omv

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

sensor.set_contrast(3)
sensor.set_saturation(3)
sensor.set_brightness(0)

print(sensor.get_gain_db())
print(sensor.get_exposure_us())

#omv.disable_fb(True)

#img = sensor.snapshot()
#img.save("test.jpg")

#img_corr = img.lens_corr(1.8)
#img_corr.save("test_corr.jpg")

# top left, top right, bottom right, bottom left
points = [(46, 6), (293, 10), (286, 240), (50, 226)]    # for QVGA
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA

black_filter = (0, 30, -128, 127, -128, 127)

while True:
    img = sensor.snapshot().lens_corr(1.5).rotation_corr(corners=points)
    blobs = img.find_blobs([black_filter])
    img.draw_rectangle(blobs[0].rect())
    #img = sensor.snapshot().lens_corr(1.5)
    #lines = img.find_line_segments()
    #print(len(lines))
    #for l in lines:
        #img.draw_line(l.line())
    #img.save('rect.jpg')
