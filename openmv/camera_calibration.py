# this script is used to calibrate the camera
import sensor
import omv

# initialize sensors
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# just to make the picture more clear
sensor.set_contrast(3)
sensor.set_saturation(3)
sensor.set_brightness(0)

print(sensor.get_gain_db())
print(sensor.get_exposure_us())

#omv.disable_fb(True)

# top left, top right, bottom right, bottom left
points = [(46, 10), (291, 6), (287, 235), (52, 228)]    # for QVGA, four corners of the arena
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA, four corners of the arena

black_filter = (0, 30, -128, 127, -128, 127)    # for detecting black puck
debug_black_filter = (0, 38, -128, 8, -128, 127)    # for detecting piece of duck tape stuck on magnet, debugging only
red_filter = (0, 100, 25, 127, -128, 127)   # for detecting red puck
mouse_filter = (0, 26, -35, 42, -32, 43)    # for detecting mouse

edges = [(274, 226), (40, 227), (36, 9), (279, 11)]

while True:
    img = sensor.snapshot().lens_corr(1.5).rotation_corr(corners=points)
    #img = sensor.snapshot().lens_corr(1.5)
    #img = sensor.snapshot()

    #continue

    blobs = img.find_blobs([mouse_filter])
    for i in range(len(blobs)):
        #print(blobs[i].cx(), blobs[i].cy())
        print(blobs[i].area())
        #if 1500 >= blobs[i].area() >= 500:
        if 2500 >= blobs[i].area() >= 300:
            img.draw_rectangle(blobs[i].rect())
            break
    print('')

    blobs = img.find_blobs([red_filter], area_threshold=10, merge=True)
    for i in range(len(blobs)):
        #print(blobs[i].area())
        if 200 >= blobs[i].area():
            img.draw_rectangle(blobs[i].rect())
            #print(blobs[i].cx(), blobs[i].cy())
            break
    #img = sensor.snapshot().lens_corr(1.5)
    #lines = img.find_line_segments()
    #print(len(lines))
    #for l in lines:
        #img.draw_line(l.line())
    #img.save('rect.jpg')
