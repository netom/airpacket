#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import random
from tqdm import tqdm

from lib import *

RMS=0.17

def gen_file(msg, snr, fname):
    signal_amp = 1.0
    noise_amp = db2a(-snr)

    symbolList = bytes2symbols(bytes.fromhex(msg))

    tones = np.zeros(44100, dtype=np.float32)
    tones[2050:-2050] = symbols2tones(symbolList, 1, 1)
    tones += noise_amp*gwn(44100)

    write_s16file(normalize(tones, RMS), fname)

for i, snr in tqdm([(i, snr) for i in range(1000) for snr in range(-10, -2)]):
    msg = ''.join(random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']) for _ in range(40))
    fname = "data/{}_{}.s16".format(msg, snr)
    gen_file(msg, snr, fname)
