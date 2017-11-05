import pyaudio
import sys
import numpy as np
import math
import time
import random

from lib import *

DEVICE = 0

if len(sys.argv) < 2:
    print("Usage: send.py <message, at most 10 characters>")
    exit()

symbolList = str2frame(sys.argv[1])

tones = []
for s in symbolList:
    tone = np.zeros(BUFFER, dtype=np.float32)
    for i in range(BUFFER):
        t = 2.0 * np.pi * i / float(RATE)
        #tone[i] = np.sign(np.sin((4410 + s * 441) * t))
        tone[i] = np.sin((4410 + s * 441) * t)

    tones = np.append(tones, tone)

#sys.stdout.write(str((tones*0x7fff).astype(np.int16).tobytes(), 'latin-1'))

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

time.sleep(len(tones)/float(RATE))

stream.stop_stream()
stream.close()

p.terminate()
