import unireedsolomon as urs
import numpy as np

RATE   = 44100
BUFFER = 200

FREQ_OFFSET = 4410
FREQ_STEP   = int(RATE/BUFFER) # 1 fft bin
FFT_OFFSET  = int(FREQ_OFFSET/FREQ_STEP)

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
# 400 nibbles, 194 data nibbles, 206 sync nibbles"""

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
1, -1, -1, 1] # 200 nibbles, 108 data nibbles, 92 sync nibbles -> 54 bytes

# Shorter code
LEN_CODE    = 54
LEN_PAYLOAD = 20

# Longer code
#LEN_CODE = 97
#LEN_PAYLOAD = 20

code = urs.rs.RSCoder(LEN_CODE, LEN_PAYLOAD) # 20 payload bytes, 34 additional bytes

symbols = list(range(17))

#print(len(syncBits))
#print(sum(map(lambda x: 1 if x == -1 else 0, syncBits)))
#print(sum(map(lambda x: 1 if x == 1 else 0, syncBits)))

def str2nibbles(s):
    ns = []
    for c in s:
        ns.append((ord(c) & 0x0f))
        ns.append((ord(c) >> 4))
    return ns

def str2frame(s):
    raw = str2nibbles(code.encode(s.rjust(LEN_PAYLOAD)))
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

def nibbles2str(f, erasures = []):
    s = ''
    for i in range(0, len(f), 2):
        o = max(0, min((f[i]-1) + (f[i+1]-1)*16, 0xff))
        s += chr(o)
    try:
        return code.decode(s, erasures)[0].strip()
    except urs.rs.RSCodecError:
        return ''

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

#print(nibbles2str(nubsync(str2frame('Hello World!'))))
