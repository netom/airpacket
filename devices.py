#!/usr/bin/env python
# -*- coding: utf8 -*-

import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i)['name'])
