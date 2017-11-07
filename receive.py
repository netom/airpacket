#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import pyaudio
import matplotlib.pyplot as plt

from lib import *

WINDOW = np.hamming

halfbuf = int(SYMBOL_LENGTH / 2)

frameLen = len(syncBits) * SYMBOL_LENGTH
halfFrameLen = 10*SYMBOL_LENGTH
oneAndHalfFrameLen = frameLen + halfFrameLen

datalen = SYMBOL_LENGTH*len(syncBits)

#generator = s16_read(datalen, 'gwn-3db.s16')
generator = pyaudio_read(datalen)

data = np.zeros(datalen*3)
while True:
    data[:datalen] = data[datalen:datalen*2]

    chunk = generator.send(None)

    if len(chunk) < datalen:
        print("End of data stream reached, terminating")
        break

    data[datalen:datalen*2] = chunk

    corr = np.correlate(normalize(data[:datalen*2]), syncSig)
    signal_strength = np.max(corr)

    if signal_strength > 2000:
        print("Got sync signal, decoding... ")
        chunk = generator.send(None)
        data[datalen*2:datalen*2+len(chunk)] = chunk
        corr = np.correlate(normalize(data), syncSig)
        signal_strength = np.max(corr)
        best_pos = np.argmax(corr)

        ns, erasures = receive_frame(data[best_pos:best_pos+len(syncSig)])
        f = nibbles2str(ns, erasures)
        if f != '':
            print("DECODED: >>>>>>>> " + f + " <<<<<<<<")
        else:
            print("NO DECODE.")

        data = np.zeros(datalen*3)

