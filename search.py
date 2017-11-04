#!/usr/bin/env python
#-*- coding: utf-8 -*-

import math
import numpy as np
import sys

SERIES_SIZE = 160

def progress(i, maxi):
    sys.stdout.write("%.3f%% \r" % (i / float(maxi) * 100))
    sys.stdout.flush()

display_map = {-1: " ", 1: "#"}
binary_map = {-1: "0", 1: "1"}
buf = np.zeros(SERIES_SIZE * 3 - 1, dtype=np.int32)
series = np.zeros(SERIES_SIZE)

best_sidelobe_value = SERIES_SIZE

best_set = set()
i = 0
maxi = 2**(SERIES_SIZE-1)
for i in range(maxi):
    if i % 10000 == 0:
        progress(i, maxi)

    # Generate a random series
    series = np.random.randint(0, 2, SERIES_SIZE) * 2 - 1

    # Execute non-cyclic autocorrelation
    buf[SERIES_SIZE:SERIES_SIZE*2] = series
    corr = np.abs(np.correlate(series, buf))

    # Zero out main lobe
    corr[SERIES_SIZE-1] = 0

    # Get the maximal sidelobe value / main lobe ratio
    max_sidelobe_value = max(corr)

    if max_sidelobe_value < best_sidelobe_value:
        best_sidelobe_value = max_sidelobe_value
        best_set = set()
        print("          \n\n" + "*" * SERIES_SIZE + " " + str(20*math.log10(best_sidelobe_value / float(SERIES_SIZE))) + " \n")

    if max_sidelobe_value == best_sidelobe_value:
        best_set.add(tuple(series))
        dm = "".join(map(lambda x: display_map[x], series))
        im = int("".join(map(lambda x: binary_map[x], series)), 2)
        print(dm, im, hex(im))
        progress(i, maxi)
