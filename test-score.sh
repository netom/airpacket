#!/bin/bash

for f in data/*.s16
do
    ./receive.py -f $f
done
