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
points = [(43, 6), (291, 11), (282, 236), (45, 225)]    # for QVGA
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA

while True:
    img = sensor.snapshot().lens_corr(1.5).rotation_corr(corners=points)
    #img = sensor.snapshot().lens_corr(1.5)
    #lines = img.find_line_segments()
    #print(len(lines))
    #for l in lines:
        #img.draw_line(l.line())
    #img.save('rect.jpg')
