#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import numpy as np

from lib import *

RMS_DEFAULT=0.17

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
    '-r', '--rms',
    metavar='RMS',
    default=RMS_DEFAULT, type=float,
    help='The root mean square of the generated signal plus noise. Default is %.3f' % RMS_DEFAULT
)
parser.add_argument(
    '-c', '--cnr',
    metavar='CNR', type=float,
    help='Carrier power to 22.05KHz band-limited white noise power ratio.'
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
    for i in range(0, len(args.message)-1, 2):
        msg += bytes([(int(args.message[i], 16) << 4) + (int(args.message[i+1], 16) & 0x0f)])
else:
    if len(args.message) > 20:
        print("A text message must be at most 20 characters.")
        exit()
    for c in args.message:
        if ord(c) > 127:
            print("A text message must only contain ASCII characters.")
            exit()
        msg += bytes([ord(c)])
    msg = msg.ljust(LEN_PAYLOAD)

signal_amp = 1.0
noise_amp  = 0.0
if args.cnr != None:
    noise_amp = db2a(-args.cnr-3) # GWNASD -> Power

symbolList = bytes2symbols(msg)

tones = symbols2tones(symbolList, 1, args.distortion)

# Calculate (estimate) carrier power, noise power, carrier to noise ratio, Eb/N0 (assuming unit impedance)
noise = noise_amp * gwn(len(tones))
pwrc  = np.average(tones**2)
pwrn  = np.average(noise**2)
if pwrn == 0:
    cnr = float('inf')
else:
    cnr   = pwrc / pwrn
fb    = 160 * (SAMPLING_RATE / len(tones)) # Channel data rate
B     = int(SAMPLING_RATE/2) # Bandwidth: whole audio spectrum

# Extend the frame to exactly 1 second
padding_len = int((SAMPLING_RATE-len(tones))/2)
padding1 = noise_amp * gwn(padding_len)
padding2 = noise_amp * gwn(padding_len)
tones = normalize(np.concatenate([padding1, tones+noise, padding2]), args.rms)

print("CNR (dB):   ", p2db(cnr))
print("Eb/N0 (dB): ", p2db(cnr*B/fb))
print("Peak:       ", np.max(np.abs(tones)))

if args.file:
    write_s16file(tones, args.file)
else:
    write_pyaudio(tones, args.device)
