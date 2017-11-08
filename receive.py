#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import numpy as np
import unireedsolomon as urs

from lib import *

parser = argparse.ArgumentParser(
    description='Listen to a pyaudio device, or read data from a file, and try to decode messages.'
)
parser.add_argument(
    '-x', '--hex',
    default=False, const=True, action='store_const',
    help='Print the message in hexadecimal instead of ASCII text.'
)
parser.add_argument(
    '-f', '--file',
    metavar='FILE', type=str,
    help='Read from this file.'
)
parser.add_argument(
    '-d', '--device',
    metavar='DEVICE', default=-1, type=int,
    help='PyAudio device index. Use devices.py to get a list of devices. The default is -1, the system-wide default device.'
)
parser.add_argument(
    '-e', '--exit-after-success',
    default=False, const=True, action='store_const',
    help='Exit after the first successfully decoded message'
)

args = parser.parse_args()

datalen = SYMBOL_LENGTH*len(syncBits)

if args.file:
    generator = s16_read(datalen, args.file)
else:
    generator = pyaudio_read(datalen, args.device)

data = np.zeros(datalen*2, dtype=np.float32)
datapos = 0
while True:
    data[:datalen] = data[datalen:]
    datapos = datalen

    chunk = generator.send(None)

    if len(chunk) == 0:
        print("End of data stream reached, terminating")
        exit(1)

    data[datapos:datapos+len(chunk)] = chunk
    datapos = datapos+len(chunk)

    corr = np.correlate(normalize(data[:datapos]), syncSig)
    signal_strength = np.max(corr)
    best_pos = np.argmax(corr)

    if signal_strength < 2000:
        continue

    print("Got sync signal, decoding... ")

    ns, erasures = receive_frame(normalize(data[best_pos:best_pos+len(syncSig)]))
    try:
        bs = nibbles2bytes(ns, erasures)
        if args.hex:
            msg = ''
            for b in bs:
                msg += "{:02x}".format(b)
        else:
            msg = str(bs, 'ASCII').strip()
        print("DECODED: >>> " + msg + " <<<")
        if args.exit_after_success:
            exit(0)
    except urs.rs.RSCodecError:
        print("NO DECODE.")
