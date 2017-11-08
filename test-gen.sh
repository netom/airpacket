#!/bin/bash

for snr in {-8..-3}
do
    for i in {1..1000}
    do
        ./send.py -s $snr -f data/${snr}_${i}.s16 "|-# Message $i #-|"
    done
done
