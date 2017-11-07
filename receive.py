#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import pyaudio
import matplotlib.pyplot as plt

from lib import *

DEVICE = -1

WINDOW = np.hamming

p = pyaudio.PyAudio()

stream = p.open(
    input_device_index = DEVICE,
    rate = SAMPLING_RATE,
    channels = 1,
    input = True,
    output = False,
    frames_per_buffer = SYMBOL_LENGTH,
    format = pyaudio.paFloat32
)

halfbuf = int(SYMBOL_LENGTH / 2)

frameLen = len(syncBits) * SYMBOL_LENGTH
#halfFrameLen = len(syncBits) * halfbuf
halfFrameLen = 10*SYMBOL_LENGTH
oneAndHalfFrameLen = frameLen + halfFrameLen

data = np.array([0] * oneAndHalfFrameLen, dtype=np.float32)

data = np.fromfile("gwn-3db.s16", dtype=np.int16).astype(np.float32) / 0x7fff

corr = np.correlate(normalize(data), syncSig)
signal_strength = np.max(corr)
best_pos = np.argmax(corr)

print(signal_strength, best_pos)

nibbles, erasures = receive_frame(data[best_pos:best_pos+len(syncSig)])
f = nibbles2str(nibbles, erasures)
if f != '':
    print("DECODED: >>>>>>>> " + f + " <<<<<<<<")
else:
    print("NO DECODE.")

exit()

datalen = SYMBOL_LENGTH*len(syncBits)
def read_data():
    return np.fromstring(
        stream.read(datalen),
        dtype=np.float32
    )

data = np.zeros(datalen*3)
while True:
    data[:datalen] = data[datalen:datalen*2]
    data[datalen:datalen*2] = read_data()

    corr = np.correlate(normalize(data[:datalen*2]), syncSig)
    signal_strength = np.max(corr)

    if signal_strength > 1000:
        print("Got sync signal, decoding... ")
        data[datalen*2:] = read_data()
        corr = np.correlate(normalize(data), syncSig)
        signal_strength = np.max(corr)
        best_pos = np.argmax(corr)

        ns, erasures = decode_frame(data[best_pos:best_pos+len(syncSig)])
        f = nibbles2str(ns, erasures)
        if f != '':
            print("DECODED: >>>>>>>> " + f + " <<<<<<<<")
        else:
            print("NO DECODE.")

        data = np.zeros(datalen*3)
