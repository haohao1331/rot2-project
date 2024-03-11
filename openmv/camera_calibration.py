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
points = [(46, 10), (291, 6), (287, 235), (52, 228)]    # for QVGA
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA

black_filter = (0, 30, -128, 127, -128, 127)
red_filter = (0, 100, 25, 127, -128, 127)
mouse_filter = (0, 26, -35, 42, -32, 43)

edges = [(274, 226), (40, 227), (36, 9), (279, 11)]

while True:
    img = sensor.snapshot().lens_corr(1.5).rotation_corr(corners=points)
    #img = sensor.snapshot().lens_corr(1.5)
    #img = sensor.snapshot()

    #continue

    #blobs = img.find_blobs([black_filter])
    #for i in range(len(blobs)):
        ##print(blobs[i].cx(), blobs[i].cy())
        ##print(blobs[i].area())
        #if 1500 >= blobs[i].area() >= 500:
            #img.draw_rectangle(blobs[i].rect())
            #break

    blobs = img.find_blobs([red_filter], area_threshold=10, merge=True)
    for i in range(len(blobs)):
        #print(blobs[i].cx(), blobs[i].cy())
        print(blobs[i].area())
        if 200 >= blobs[i].area():
            img.draw_rectangle(blobs[i].rect())
            break
    #img = sensor.snapshot().lens_corr(1.5)
    #lines = img.find_line_segments()
    #print(len(lines))
    #for l in lines:
        #img.draw_line(l.line())
    #img.save('rect.jpg')
