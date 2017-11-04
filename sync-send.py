import pyaudio
import sys
import numpy as np
import math
import time
import random
import matplotlib.pyplot as plt

from lib import *

DEVICE = 0
RATE   = 44100
BUFFER = 100

p = pyaudio.PyAudio()

symbolList = str2frame('hello')

tones = []
for b in syncBits:
    tone = np.zeros(BUFFER, dtype=np.float32)

    if b == 1:
        for i in range(BUFFER):
            t = 2.0 * np.pi * i / float(RATE)
            #tone[i] = np.sign(np.sin((4410 + s * 441) * t))
            tone[i] = np.sin((4410 + 0 * 441) * t)

    tones = np.append(tones, tone)

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

time.sleep(len(tones)*2/float(RATE))

stream.stop_stream()
stream.close()

p.terminate()

plt.plot(tones)
plt.show()
