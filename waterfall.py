#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy
import pyaudio
import matplotlib.pyplot
import matplotlib.animation

RATE        = 44100
FFTPOINTS   = 1000
VALUEPOINTS = 1000
OVERLAP     = 0
CENTERFREQ  = 6200
BANDWIDTH   = 4000
WINDOW      = numpy.hamming
WIDTH       = 128
GAIN        = 2000


RESOLUTION = RATE/float(FFTPOINTS)
START      = int(CENTERFREQ/RESOLUTION-BANDWIDTH/2/RESOLUTION)
END        = int(CENTERFREQ/RESOLUTION+BANDWIDTH/2/RESOLUTION)
HEIGHT     = END-START
FRAME      = VALUEPOINTS-OVERLAP

def init_image():
    im.set_array(numpy.zeros((HEIGHT, WIDTH), dtype=numpy.float32))
    return (im,)

def update_image(i):
    data[0:OVERLAP] = data[VALUEPOINTS-OVERLAP:VALUEPOINTS]

    data[OVERLAP:VALUEPOINTS] = numpy.fromstring(
        stream.read(FRAME),
        dtype=numpy.float32
    )

    fft = numpy.fft.rfft(data*WINDOW(len(data)))[START:END] / FFTPOINTS * GAIN

    line = numpy.sqrt(numpy.real(fft)**2+numpy.imag(fft)**2)

    im_data[:,:WIDTH-1] = im_data[:,1:]
    im_data[:,WIDTH-1] = line
    im.set_array(im_data)
    return (im,)

fig = matplotlib.pyplot.figure()

p = pyaudio.PyAudio()

stream = p.open(
    rate = RATE,
    channels = 1,
    input = True,
    output = False,
    frames_per_buffer = FRAME,
    format = pyaudio.paFloat32
)

im_data = numpy.zeros((HEIGHT, WIDTH), dtype=numpy.float32)

im = matplotlib.pyplot.imshow(im_data, cmap=matplotlib.pyplot.get_cmap('gray'), norm=matplotlib.colors.LogNorm(vmin=0.01, vmax=1))
im.set_clim(0.01, 1.0)

data = numpy.zeros(FFTPOINTS, dtype=numpy.float32)

ani = matplotlib.animation.FuncAnimation(
    fig, update_image, init_func=init_image,
    interval=0, blit=True)

matplotlib.pyplot.show()
