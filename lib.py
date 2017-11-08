import numpy as np
import pyaudio
import time
import unireedsolomon as urs

# Audio sampling rate
SAMPLING_RATE   = 44100

# Length of a symbol in audio samples.
# Must divide SAMPLING_RATE with zero remainder 
SYMBOL_LENGTH = 200

# The lowest frequency in a symbol
FREQ_OFFSET = 4410
FREQ_STEP   = SAMPLING_RATE/SYMBOL_LENGTH # 1 fft bin
FFT_OFFSET  = int(FREQ_OFFSET/FREQ_STEP)

# Number of requencies to use. This cannot be modified easily,
# since the decoding process makes the assumption that a nibble
# is encoded in a single symbol.
CPMSK_N = 17

# Experimental 400 symbol long sync sequence
# 400 nibbles, 194 data nibbles, 206 sync nibbles -> 97 bytes
"""syncBits = [1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, 1, 1, -1, 1, 1, -1, 
-1, 1, -1, -1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, -1, 1, 
1, 1, 1, -1, -1, 1, 1, 1, -1, -1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 
1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, 
1, 1, 1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 
-1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 1, -1, 1, 
1, 1, -1, 1, -1, -1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 
-1, -1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, 1, 1, 1, -1, 1, 1, 1, 
1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 
1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1, 1, -1, 1, 
-1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 
-1, -1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, 1, -1, 
1, -1, 1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, 1, -1, -1, 1, 1, 
-1, 1, -1, 1, 1, -1, -1, -1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, 1, 
-1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, 1, 1, 
1, -1, 1, -1, 1, -1, 1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 
-1, -1, 1, -1, -1, -1, 1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1, -1, 
-1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 
1, -1, -1, -1, 1, 1, -1, -1, 1, 1, 1, -1, -1, -1, -1, 1, -1, 1, 1, -1, 
-1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, -1, -1, -1, -1, -1]
LEN_CODE = 97
LEN_PAYLOAD = 20
"""

# Experimental 200 symbol long sync sequence
# 200 nibbles, 108 data nibbles, 92 sync nibbles -> 54 bytes
syncBits = [1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, 1, 
1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1, 1, 
-1, -1, -1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, 
1, -1, 1, 1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 
-1, 1, 1, 1, 1, -1, 1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, 1, 
1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, -1, -1, 1, 1, -1, -1, -1, -1, 
-1, 1, -1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 
1, -1, -1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, 1, -1, 1, 1, 
-1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 
-1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1, 
1, -1, -1, 1]
LEN_CODE    = 54
LEN_PAYLOAD = 20


def nibbles(s):
    """Chops up an iterable of int-ables to nibbles"""
    ns = []
    for c in s:
        ns.append((int(c) & 0x0f))
        ns.append((int(c) >> 4))
    return ns

def bytes2symbols(bs):
    raw = nibbles(code.encode(bs, return_string=False))
    ret = []
    i = 0
    for b in syncBits:
        if b == 1:
            ret.append(0)
        else:
            ret.append(raw[i] + 1)
            i += 1
    return ret

def nubsync(f):
    return list(map(lambda x: x[1], filter(lambda x: x[0] == -1, zip(syncBits, f))))

def nibbles2bytes(ns, erasures = []):
    b = b''
    for i in range(0, len(ns), 2):
        o = max(0, min((ns[i]-1) + (ns[i+1]-1)*16, 0xff))
        b += bytes([o])
    decoded = bytes(map(int, code.decode(b, erasures, return_string=False)[0]))
    return decoded

def gwn(size, std=1, mean=0):
    """Gaussian white noise"""
    return np.random.normal(mean, std, size=size)

def db2a(db):
    """Returns a ratio of amplitude"""
    return 10.0**(db/20.0)

def a2db(a):
    """Returns decibel of amplitude ratio"""
    return 20.0*np.log10(a)

def p2db(a):
    """Returns decibel of power ratio"""
    return 10.0*np.log10(a)

def write_s16file(f32data, fname):
    (f32data*0x7fff).astype(np.int16).tofile(fname)

def write_pyaudio(f32data, device=-1):
    p = pyaudio.PyAudio()

    stream = p.open(
        output_device_index = device,
        format = pyaudio.paFloat32,
        channels = 1,
        rate = SAMPLING_RATE,
        input = False,
        output = True,
        frames_per_buffer = SYMBOL_LENGTH
    )

    stream.write(f32data.astype(np.float32).tostring(), len(f32data))

    time.sleep(len(f32data)/float(SAMPLING_RATE)*0.5)

    stream.stop_stream()
    stream.close()

    p.terminate()

def sinBuf():
    tone = np.zeros(SYMBOL_LENGTH, dtype=np.float32)
    for i in range(SYMBOL_LENGTH):
        t = 2.0 * np.pi * i / float(SAMPLING_RATE)
        tone[i] = np.sin(FREQ_OFFSET * t)
    return tone

def normalize(x, rms=1.0):
    return x / np.sqrt(np.sum(np.abs(x)**2) / len(x)) * rms

def symbols2tones(symbolList, amplitude=1.0, distortion=1.0):
    tones = np.zeros(SYMBOL_LENGTH*len(symbolList), dtype=np.float32)
    for j in range(len(symbolList)):
        s = symbolList[j]
        for i in range(SYMBOL_LENGTH):
            t = 2.0 * np.pi * i / float(SAMPLING_RATE)
            tones[SYMBOL_LENGTH*j+i] = np.clip(distortion * amplitude * np.sin((FREQ_OFFSET + s * FREQ_STEP) * t), -amplitude, amplitude)

    return tones

def receive_frame(frame, dft_window = None):
    syms = []
    erasures = []
    j = 0
    ffts = []
    for i in range(len(syncBits)):
        if dft_window != None:
            fft = np.absolute(np.fft.rfft(frame[i*SYMBOL_LENGTH:(i+1)*SYMBOL_LENGTH]*dft_window(SYMBOL_LENGTH))[FFT_OFFSET:FFT_OFFSET+CPMSK_N+1])
        else:
            fft = np.absolute(np.fft.rfft(frame[i*SYMBOL_LENGTH:(i+1)*SYMBOL_LENGTH]                          )[FFT_OFFSET:FFT_OFFSET+CPMSK_N+1])
        ffts.append(fft)

        if syncBits[i] == 1:
            continue

        bestpos = np.argmax(fft)
        best = fft[bestpos]

        fft[bestpos] = 0

        bestpos2 = np.argmax(fft)
        best2 = fft[bestpos2]

        syms.append(bestpos)

        #if best-best2 < 0.1: # Colud be much smarter. Also: soft decode.
        #    erasures.append(j)
        #j += 1

    #print(len(erasures))
    #plt.imshow(ffts)
    #plt.show()
    return (syms, erasures)

def pyaudio_read(samples, device=-1):
    p = pyaudio.PyAudio()

    stream = p.open(
        input_device_index = device,
        rate = SAMPLING_RATE,
        channels = 1,
        input = True,
        output = False,
        frames_per_buffer = SYMBOL_LENGTH,
        format = pyaudio.paFloat32
    )

    while True:
        yield np.fromstring(
            stream.read(samples),
            dtype=np.float32
        )

def s16_read_all(filename, offset=0):
    return (np.fromfile(filename, dtype=np.int16).astype(np.float32) / 0x7fff)[offset:]

def s16_read(samples, filename):
    data = s16_read_all(filename)
    i = 0
    while True:
        yield data[i*samples:(i+1)*samples]
        i += 1

code = urs.rs.RSCoder(LEN_CODE, LEN_PAYLOAD)

symbols = list(range(CPMSK_N))

syncSig = normalize(np.concatenate(list(map(lambda x: sinBuf()*x, syncBits))))

#print(len(syncBits))
#print(sum(map(lambda x: 1 if x == -1 else 0, syncBits)))
#print(sum(map(lambda x: 1 if x == 1 else 0, syncBits)))

#print(nibbles2str(nubsync(str2frame('Hello World!'))))
