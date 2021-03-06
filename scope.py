#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np

from lib import *

parser = argparse.ArgumentParser(
    description='View the waveform, DFT, or waterfall chart of data stored in s16 files. It shows the waveform by default.'
)
parser.add_argument(
    'file',
    metavar='FILE', type=str,
    help='The file to read'
)
parser.add_argument(
    '-s', '--spectrum',
    default=False, const=True, action='store_const',
    help='Show the spectrum'
)
parser.add_argument(
    '-c', '--correlation',
    default=False, const=True, action='store_const',
    help='Show correlation with the synchronization vector'
)
parser.add_argument(
    '-w', '--waterfall',
    default=False, const=True, action='store_const',
    help='Show a waterfall chart'
)
parser.add_argument(
    '-o', '--offset',
    default=0, type=int,
    help='Skip this many samples at the beginning of the file'
)
parser.add_argument(
    '-y', '--sync',
    default=False, const=True, action='store_const',
    help='Try to synchronize to a packet'
)


args = parser.parse_args()

data = normalize(s16_read_all(args.file, args.offset))

if args.sync:
    corr = np.correlate(data, syncSig)
    signal_strength = np.max(corr)
    best_pos = np.argmax(corr)
    data = data[best_pos:best_pos+len(syncSig)]

if args.spectrum:
    fft = np.absolute(np.fft.rfft(data))/np.sqrt(len(data))
    fft[:1000] = 0 # Zero out the first 1KHz
    plt.plot(fft)
elif args.waterfall:
    ffts = []
    for i in range(int(len(data)/SYMBOL_LENGTH)):
        fft = np.absolute(np.fft.rfft(data[i*SYMBOL_LENGTH:(i+1)*SYMBOL_LENGTH])/SYMBOL_LENGTH)
        fft[:5] = 0 # Zero out the first 1KHz
        ffts.append(fft)
    plt.imshow(ffts)
elif args.correlation:
    corr = np.correlate(data, syncSig)
    plt.plot(corr)
else:
    plt.plot(data)

plt.show()

