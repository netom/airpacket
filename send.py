#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import numpy as np
import math
import random
import matplotlib.pyplot as plt

from lib import *

AMP    = 0.03
NOISE  = AMP*db2a(8)

sys.argv.append("űű Hello World!")

if len(sys.argv) < 2:
    print("Usage: send.py <message, at most 10 characters>")
    exit()

symbolList = str2frame(sys.argv[1][:20])

tones = symbols2tones(symbolList, AMP)

# Calculate (estimate) carrier power, noise power, carrier to noise ratio, Eb/N0 (assuming unit impedance)
pwrc = np.average(tones**2)
pwrn = np.average((NOISE * gwn(len(tones)))**2)
cnr  = pwrc / pwrn
fb   = 160 * (SAMPLING_RATE / len(tones)) # Channel data rate
B    = int(SAMPLING_RATE/2) # Bandwidth: whole audio spectrum
print("Carrier power:", pwrc)
print("Noise power:  ", pwrn)
print("CNR (dB):     ", p2db(cnr))
print("Net bit rate: ", fb)
print("Bandwidth:    ", B)
print("Eb/N0 (dB):   ", p2db(cnr*B/fb))

# Extend the frame to exactly 1 second
padding = [0]*int((SAMPLING_RATE-len(tones))/2)
tones = np.concatenate([padding, tones, padding])
tones += NOISE * gwn(len(tones))

print("Peak:         ", np.max(np.abs(tones)))

#fft = np.absolute(np.fft.rfft(tones))**2/len(tones) # This estimates PSD, power/hz
fft = np.absolute(np.fft.rfft(tones))/np.sqrt(len(tones)) # Shows amplitude
#print(np.average(fft))
#plt.plot(tones)
#plt.show()

write_s16file("gwn-3db.s16", tones)
#write_pyaudio(tones)
