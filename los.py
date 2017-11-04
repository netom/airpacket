#!/usr/bin/env python
# -*- coding: utf-8 -*-

# n=105-re a PSL=-26.4444 egy papírban. Nem rossz.

import math
import numpy
import random
import matplotlib.pyplot as plt

from lib import *

best_so_far = syncBits

VECTOR_LEN = len(best_so_far)

def random_vector(l):
    return numpy.random.randint(0, 2, l) * 2 - 1

def tweak(v):
    v = numpy.copy(v)
    i = random.randint(0, len(v)-1)
    v[i] = -v[i]
    return v

# Returns all non-trivial non-circular shift autocorrelation coefficients
def autocorrelate(v):
    return numpy.correlate(v, v, mode='full')[:len(v)-1]

def energy(v):
    c = numpy.abs(autocorrelate(v))
    return numpy.max(c)

def psl(v):
    c = numpy.abs(autocorrelate(v))
    return numpy.max(c)

def psldb(v):
    return 20 * numpy.log10(psl(v) / VECTOR_LEN)

def next_vec(v1, t):
    v2 = tweak(v1)
    q1 = energy(v1)
    q2 = energy(v2)

    if q2 < q1:
        return v2

    p = math.exp(-(q2-q1)/t)
    
    return v2 if random.random() < p else v1

def neighbour_search(v):
    bestv = v
    bestpsl = psl(v)
    for i in range(len(v)):
        vv = numpy.copy(v)
        vv[i] = -vv[i]
        pslvv = psl(vv) # TODO: optimize this
        if pslvv < bestpsl:
            bestv = vv
            bestpsl = pslvv
    return (bestv, bestpsl)

def hillclimb(v):
    bestv = v
    bestpsl = psl(bestv)
    while True:
        (vv, pslvv) = neighbour_search(bestv)
        if pslvv < bestpsl:
            bestpsl = pslvv
            bestv = vv
            continue
        break
    return (bestv, bestpsl)
        

VECTOR_LEN = 126

bestv = best_so_far
bestpsl = psl(bestv)

bests = set()
bests.add(tuple(bestv))

while True:
    v = random_vector(VECTOR_LEN)
    for i in range(VECTOR_LEN):
        v = numpy.roll(v, 1)
        (vv, pslvv) = hillclimb(v)
        #print psl(v), pslvv, 20 * numpy.log10(float(pslvv) / VECTOR_LEN)
        if pslvv <= bestpsl and (tuple(vv) not in bests):
            bestpsl = pslvv
            bestv = vv
            bests.add(tuple(bestv))
            print(bestpsl, 20 * numpy.log10(float(bestpsl) / VECTOR_LEN), list(bestv))
    print(".")
 
#print("###", bestpsl, bestv, autocorrelate(bestv))

#plt.plot(numpy.correlate(v, v, mode='full'))
#plt.show()
