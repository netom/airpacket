#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import sys
import numpy as np

from lib import *

AMPDEFAULT=0.15

parser = argparse.ArgumentParser(
    description='Create a modulated packet that encodes a string or hex symbols.'
)
parser.add_argument(
    'message',
    metavar='MSG', type=str,
    help='the message to send. Less than 20 character *ASCII* text, or exactly 40 hexa digits.'
)
parser.add_argument(
    '-x', '--hex',
    default=False, const=True, action='store_const',
    help='The message is a string of hexadecimal digits.'
)
parser.add_argument(
    '-f', '--file',
    metavar='FILE', type=str,
    help='Write into file instead of playing the audio.'
)
parser.add_argument(
    '-a', '--amp',
    metavar='AMP',
    default=AMPDEFAULT, type=float,
    help='Average amplitude of signal plus noise. Default is %.3f' % AMPDEFAULT
)
parser.add_argument(
    '-s', '--snr',
    metavar='SNR', type=float,
    help='Signal to noise amplitude ratio (SNR), expressed in decibels amplitude. Adds white noise.'
)
parser.add_argument(
    '-t', '--distortion',
    metavar='DISTORTION', default=1.0, type=float,
    help='Distortion. Multiply the signal with this number, and clip to the original amplitude.'
)
parser.add_argument(
    '-d', '--device',
    metavar='DEVICE', default=-1, type=int,
    help='PyAudio device index. Use devices.py to get a list of devices. THe default is -1, the system-wide default device.'
)

args = parser.parse_args()

msg = b''
if args.hex:
    if len(args.message) != 40:
        print("A hexadecimal message must be exactly 40 digit long.")
        exit()
    for c in args.message:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            print('The -x flag was issued, yet the message contains a non-hexadecimal character "%s".' % c)
            exit()
    for i in range(len(args.message)-1):
        msg += bytes([(int(args.message[i], 16) & 0xf) + (int(args.message[i+1], 16) << 4)])
else:
    if len(args.message) > 20:
        print("A text message must be at most 20 characters.")
        exit()
    for c in args.message:
        if ord(c) > 127:
            print("A text message must only contain ASCII characters.")
            exit()
        msg += bytes([ord(c)])
    msg.ljust(LEN_PAYLOAD)

signal_amp = args.amp
noise_amp  = 0
if args.snr != None:
    alpha      = np.sqrt(db2a(args.snr))
    signal_amp = args.amp * alpha
    noise_amp  = args.amp / alpha

if len(sys.argv) < 2:
    print("Usage: send.py <message, at most 10 characters>")
    exit()

symbolList = bytes2symbols(msg)

tones = symbols2tones(symbolList, signal_amp, args.distortion)

# Calculate (estimate) carrier power, noise power, carrier to noise ratio, Eb/N0 (assuming unit impedance)
noise = noise_amp * gwn(len(tones))
pwrc  = np.average(tones**2)
pwrn  = np.average(noise**2)
cnr   = pwrc / pwrn
fb    = 160 * (SAMPLING_RATE / len(tones)) # Channel data rate
B     = int(SAMPLING_RATE/2) # Bandwidth: whole audio spectrum

print("Carrier power:", pwrc)
print("Noise power:  ", pwrn)
print("CNR (dB):     ", p2db(cnr))
print("Net bit rate: ", fb)
print("Bandwidth:    ", B)
print("Eb/N0 (dB):   ", p2db(cnr*B/fb))

# Extend the frame to exactly 1 second
padding = [0]*int((SAMPLING_RATE-len(tones))/2)
tones = np.concatenate([padding, tones, padding])
tones += noise_amp * gwn(len(tones))

print("Peak:         ", np.max(np.abs(tones)))

#fft = np.absolute(np.fft.rfft(tones))**2/len(tones) # This estimates PSD, power/hz
fft = np.absolute(np.fft.rfft(tones))/np.sqrt(len(tones)) # Shows amplitude
#print(np.average(fft))
#plt.plot(tones)
#plt.show()

if args.file:
    write_s16file(tones, args.file)
else:
    write_pyaudio(tones, args.device)
