import pickle
import numpy as np

def from_file(fname):
    """
    G-code files are modified versions of https://github.com/grbl/grbl/wiki/G-Code-Examples.
    """
    f = open(fname, 'r')
    gc = f.read().split('\n')
    f.close()
    return gc

import math


def variable_feed_lissajous(a, b, delta, feed, cyc):
    """Generate list of G-code for motion along a Lissajous curve.

    Parameters
    ----------
    a : (float) Frequency ratio of the first oscillation.
    b : (float) Frequency ratio of the second oscillation.
    delta : (float) Phase difference between the two oscillations in radians.
    feed : (int) Feed rate in inch/min.
    cyc : (int) Number of repeats.

    Returns
    -------
    g : (list) List of G-code."""
    g = []
    g.append('G17 G20 G90 G94')  # inches
    g.append('G01 X0 Y0 F' + str(feed))

    for _ in range(cyc):
        t = 0.0
        while t <= 2 * math.pi:
            x = math.sin(a * t)
            y = math.sin(b * t + delta)

            g.append('G01 X' + str(x) + ' Y' + str(y) + ' F' + str(feed))

            t += 0.01  # Increment the parameter value for smoother curve

    g.append('G01 X0 Y0 F' + str(feed))
    return g


def chirp(L, A, f1, f2, deltaX):
    gcode = []

    # Header
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Absolute positioning")
    gcode.append("G17 ; XY plane")
    gcode.append("G28 ; Home all axes")
    gcode.append("G92 X0 Y0 ; Set current position to (0, 0)")
    gcode.append("M03 ; Start spindle or laser")
    gcode.append("G01 F100 ; Set feed rate to 100mm/min")

    # Generate chirp pattern
    X = 0
    while X <= L:
        Y = A * np.sin(2 * np.pi * (f1 + (f2 - f1) * X / L) * X)
        gcode.append(f"G01 X{X:.4f} Y{Y:.4f}")
        X += deltaX

    # Footer
    gcode.append("M05 ; Stop spindle or laser")
    gcode.append("G28 ; Home all axes")

    return gcode



def variable_feed_filleted_square(side_length, feed, radius, cyc):
    """Generate list of G-code for filleted square motion.

    Parameters
    ----------
    side_length : (int) Length of the square sides.
    feed : (int) Feed rate in inch/min.
    radius : (int) Fillet radius.
    cyc : (int) Number of repeats.

    Returns
    -------
    g : (list) List of G-code."""
    g = []
    g.append('G17 G20 G90 G94')  # inches

    # Starting point same as end point in cycle
    g.append(f'G01 X0 Y{radius} F{feed}')

    for _ in range(cyc):
        g.append(f'G01 X{side_length - radius} Y0 F{feed}')
        g.append(f'G03 X{side_length} Y{radius} I0 J{radius} F{feed}')

        g.append(f'G01 X{side_length} Y{side_length - radius} F{feed}')
        g.append(f'G03 X{side_length - radius} Y{side_length} I{-radius} J{0} F{feed}')
        
        g.append(f'G01 X{radius} Y{side_length} F{feed}')
        g.append(f'G03 X0 Y{side_length - radius} I{0} J{-radius} F{feed}')
        
        g.append(f'G01 X0 Y{radius} F{feed}')
        g.append(f'G03 X{radius} Y0 I{radius} J{0} F{feed}')

    return g


def variable_feed_rectangle(length, width, feeds, cyc):
    """Generate list of G-code for rectangle motion.

    Parameters
    ----------
    length : (int) Length of the rectangle.
    width : (int) Width of the rectangle.
    feed : (array) Feed rates in inch/min, will alternate through in order.
    cyc : (int) Number of repeats.

    Returns
    -------
    g : (list) List of G-code."""
    feed = feeds[0]
    g = []
    g.append('G17 G20 G90 G94')  # inches
    g.append('G01 X0 Y0 F' + str(feed))

    for i in range(cyc):
        feed = feeds[i%len(feeds)]
        g.append('G01 X' + str(length) + ' F' + str(feed))
        g.append('G01 Y' + str(width) + ' F' + str(feed))
        g.append('G01 X' + str(-length) + ' F' + str(feed))
        g.append('G01 Y' + str(-width) + ' F' + str(feed))
    g.append('G01 X0 Y0 F' + str(feeds[0]))    
    return g   


def variable_feed_circle(feed1, feed2, cyc, r):
    """
    Generate list of g-code for rotary motion.

    Parameters
    ----------
    feed : int
        Feed rate in inch/min.
    cyc : int
        Number of repeats.
    r : int
        Radius.

    Returns
    -------
    g : list
        List of G-code.

    """
    g = []
    g.append('G17 G20 G90 G94') # inches
    g.append('G00 X' + str(-r) + f' Y0 F{feed1}')
    for c in range(cyc):
        
        feed = feed1 if c % 2 else feed2

        g.append('G02 X0 Y' + str(r) + ' I' + str(r) + ' J0 F' + str(feed))
        g.append('X' + str(r) + ' Y0 I0 J' + str(-r))
        g.append('X0 Y' + str(-r) + ' I' + str(-r) + ' J0')
        g.append('X' + str(-r) + ' Y0 I0 J' + str(r))
    g.append(f'G00 X0 Y0 F{feed}') 
    return g

def circle(feed, cyc, r):
    """
    Generate list of g-code for rotary motion.

    Parameters
    ----------
    feed : int
        Feed rate in inch/min.
    cyc : int
        Number of repeats.
    r : int
        Radius.

    Returns
    -------
    g : list
        List of G-code.

    """
    g = []
    g.append('G17 G20 G90 G94') # inches
    g.append('G00 X' + str(-r) + f' Y0 F{feed}')
    for c in range(cyc):
        g.append('G02 X0 Y' + str(r) + ' I' + str(r) + ' J0 F' + str(feed))
        g.append('X' + str(r) + ' Y0 I0 J' + str(-r))
        g.append('X0 Y' + str(-r) + ' I' + str(-r) + ' J0')
        g.append('X' + str(-r) + ' Y0 I0 J' + str(r))
    g.append(f'G00 X0 Y0 F{feed}') 
    return g




def fake_mouse(nickname, bo, cyc):
    """
    Generate list of g-code from trajectory files in Rosenberg-2021 paper.

    Parameters
    ----------
    nickname : str
        Mouse.
    bo : int
        Bout.
    cyc : int
        Number of repeats.

    Returns
    -------
    g : list
        List of G-code.

    """
    import sys
    module_path = r'C:\git\mouse-tracker\grblGantry\grblGantry\Rosenberg_2021' 
    # if module_path not in sys.path:
    #     sys.path.append(module_path)

    with open(module_path+"\\"+nickname+'-tf', 'rb') as f:
        tf = pickle.load(f)
    print(tf)
    tr = tf.ke[bo]
    tr = tr[~np.isnan(tr).any(axis=1)] * 22.5 # 1 unit = 22.5 inches (length of maze), but length of gantry is 16
    tr = tr - np.amin(tr, axis=0) # normalize
    _, ymax = np.amax(tr, axis=0)
    
    if ymax >= 12:
        print('bad trajectory') # cnc x-axis length <= 12
        return ['']
    sf = 0.2 # in small gantry, 1 "inch" = 5 inches
    af = 10 # sampling rate

    tr = tr * sf
    spd = np.diff(tr, axis=0) * 30 * 60 # speed (inch/min); frame rate 30 Hz
    spd[:, 0] = np.convolve(spd[:, 0], np.ones(af)/af, mode='same') # average speed every af frames
    spd[:, 1] = np.convolve(spd[:, 1], np.ones(af)/af, mode='same')
    tr[:, 0] = tr[:, 0]/22.5*16
    feeds = []
    g = []
    g.append('G17 G20 G90 G94') # inches
    for c in range(cyc):
        g.append('G00 X' + str(tr[0, 1]) + ' Y' + str(tr[0, 0]))
        for step in range(0, len(tr)-1, af):
            feed = np.linalg.norm(spd[step, :])
            g.append('G01 X' + str(tr[step+1, 1]) + ' Y' + str(tr[step+1, 0]) + ' F' + str(feed))
            # g.append('G00 X' + str(tr[step+1, 1]) + ' Y' + str(tr[step+1, 0]))
            feeds.append(feed)
        g.append('G00 X0 Y0')
    return g, feeds

    
    
