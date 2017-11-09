#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import os
from tqdm import tqdm

from lib import *

def plus(d, k):
    d[k] = d.get(k, 0) + 1

files = {}
good_decodes = {}
no_decodes = {}
bad_decodes = {}
good_syncs = {}
bad_syncs = {}
bad_sync_set = set()

for fname in tqdm(os.listdir('data')):
    if fname[-4:] != '.s16':
        continue

    msg, snr = fname.split('.')[0].split('_')
    snr = int(snr)

    plus(files, snr)

    fname = 'data/' + fname

    data = np.fromfile(fname, dtype=np.int16).astype(np.float32) / 0x7fff

    corr = np.correlate(normalize(data), syncSig)
    signal_strength = np.max(corr)
    best_pos = np.argmax(corr)

    if best_pos == 2050:
        plus(good_syncs, snr)
    else:
        plus(bad_syncs, snr)
        bad_sync_set.add(best_pos)

    ns, erasures = receive_frame(normalize(data[best_pos:best_pos+len(syncSig)]))

    try:
        bs = nibbles2bytes(ns, erasures)

        msg2 = ''
        for b in bs:
            msg2 += "{:02x}".format(b)

        if msg == msg2:
            plus(good_decodes, snr)
        else:
            plus(bad_decodes, snr)
    except urs.rs.RSCodecError:
        plus(no_decodes, snr)

print('FILES:        ', files)
print('GOOD DECODES: ', good_decodes)
print('NO DECODES:   ', no_decodes)
print('BAD DECODES:  ', bad_decodes)
print('GOOD SYNCS:   ', good_syncs)
print('BAD SYNCS:    ', bad_syncs)
print('BAD SYNC SET: ', bad_sync_set)
