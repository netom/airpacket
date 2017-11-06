#!/usr/bin/env python
# -*- coding: utf8 -*-

import pyaudio
import sys
import numpy as np
import math
import time
import random
import matplotlib.pyplot as plt

from lib import *

DEVICE = -1
AMP    = 0.2
NOISE  = AMP*dba(3)

sys.argv.append("hello")

if len(sys.argv) < 2:
    print("Usage: send.py <message, at most 10 characters>")
    exit()

symbolList = str2frame(sys.argv[1][:20])

tones = []
for s in symbolList:
    tone = np.zeros(BUFFER, dtype=np.float32)
    for i in range(BUFFER):
        t = 2.0 * np.pi * i / float(RATE)
        #tone[i] = AMP * np.sign(np.sin((4410 + s * 441) * t))
        tone[i] = AMP * np.sin((4410 + s * 441) * t)

    tones = np.append(tones, tone)

tones = np.concatenate([[0]*random.randint(1000, 50000), tones, [0]*random.randint(1000, 50000)])
tones += NOISE * gwn(len(tones))

#fft = np.absolute(np.fft.rfft(tones))
#plt.plot(fft)
#plt.show()

(tones*0x7fff).astype(np.int16).tofile("gwn-3db.s16")

exit()


p = pyaudio.PyAudio()

stream = p.open(
    output_device_index = DEVICE,
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = False,
    output = True,
    frames_per_buffer = BUFFER
)

stream.write(tones.astype(np.float32).tostring(), len(tones))

time.sleep(len(tones)/float(RATE)*0.5)

stream.stop_stream()
stream.close()

p.terminate()
