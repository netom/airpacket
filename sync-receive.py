#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import pyaudio
import matplotlib.pyplot as plt

from lib import *

RATE   = 44100
FRAME  = 100
WINDOW = np.hamming

p = pyaudio.PyAudio()

stream = p.open(
    rate = RATE,
    channels = 1,
    input = True,
    output = False,
    frames_per_buffer = FRAME,
    format = pyaudio.paFloat32
)

halfbuf = int(BUFFER / 2)

frameLen = len(syncBits) * BUFFER
#halfFrameLen = len(syncBits) * halfbuf
halfFrameLen = 10*BUFFER
oneAndHalfFrameLen = frameLen + halfFrameLen

data = np.array([0] * oneAndHalfFrameLen, dtype=np.float32)

def sinBuf():
    tone = np.zeros(BUFFER, dtype=np.float32)
    for i in range(BUFFER):
        t = 2.0 * np.pi * i / float(RATE)
        #tone[i] = np.sign(np.sin((4410 + s * 441) * t))
        tone[i] = np.sin((4410 + 0 * 441) * t)
    return tone

def normalize(x):
    return x / np.max(np.abs(x))

def decode_frame(f):
    syms = []
    erasures = []
    j = 0
    ffts = []
    for i in range(len(syncBits)):
        fft = np.absolute(np.fft.rfft(f[i*BUFFER:(i+1)*BUFFER])[10:28])
        ffts.append(fft)

        if syncBits[i] == 1:
            continue

        bestpos = np.argmax(fft)
        best = fft[bestpos]

        fft[bestpos] = 0

        bestpos2 = np.argmax(fft)
        best2 = fft[bestpos2]

        syms.append(bestpos)

        if best-best2 < 0.005:
            erasures.append(j)
        j += 1

    plt.imshow(ffts)
    plt.show()
    return (syms, erasures)

syncSig = np.concatenate(list(map(lambda x: sinBuf()*x, syncBits)))

curr = prev = 0.0
climbing = False
while True:
    data[:frameLen+BUFFER*5] = data[BUFFER*5:]
    data[frameLen+BUFFER*5:] = np.fromstring(
        stream.read(BUFFER*5),
        dtype=np.float32
    )

    corr = np.abs(np.correlate(normalize(data), syncSig))
    curr = np.max(corr)
    argm = np.argmax(corr)

    if prev == curr and curr > 500:
        print("FRAME??? " + str(curr) + " " + str(argm))
        ns, erasures = decode_frame(data[argm:argm+len(syncSig)])
        f = nibbles2str(ns, erasures)
        if f != '':
            print(f)

    prev = curr
