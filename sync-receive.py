#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy
import pyaudio

from lib import *

RATE   = 44100
FRAME  = 100
WINDOW = numpy.hamming

p = pyaudio.PyAudio()

stream = p.open(
    rate = RATE,
    channels = 1,
    input = True,
    output = False,
    frames_per_buffer = FRAME,
    format = pyaudio.paFloat32
)

data = numpy.zeros(FRAME, dtype=numpy.float32)

frame = [0] * 100

while True:
    data[:] = numpy.fromstring(
        stream.read(FRAME),
        dtype=numpy.float32
    )

    fft = numpy.absolute(numpy.fft.rfft(data))

    frame[:-1] = frame[1:]
    frame[-1] = numpy.argmax(fft[10:28])
    s = frame2str(frame)
    if s != '':
        print(s)