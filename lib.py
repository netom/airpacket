import unireedsolomon as urs

RATE   = 44100
BUFFER = 100

code = urs.rs.RSCoder(29,19) # 20 payload bytes, 19 additional bytes

syncBits = [
    1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1,  1,  1, -1,  1,  1,
    1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1,  1,  1, -1,  1,  1,
    1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1, 
   -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1,  1,  1, -1,
    1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1,  1, -1,  1,
   -1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1, -1,
    1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1,
    1,  1, -1,  1, -1, -1, -1
] # 58 data bits, 68 sync bits

symbols = list(range(17))

#print(sum(map(lambda x: 0 if x == -1 else 1, syncBits)))

def str2nibbles(s):
    ns = []
    for c in s:
        ns.append((ord(c) & 0x0f))
        ns.append((ord(c) >> 4))
    return ns

def str2frame(s):
    raw = str2nibbles(code.encode(s.rjust(10)))
    ret = []
    i = 0
    for b in syncBits:
        if b == 1:
            ret.append(0)
        else:
            ret.append(raw[i] + 1)
            i += 1
    return ret

def frame2str(f):
    s = ''
    f2 = list(map(lambda x: x[1], filter(lambda x: x[0] == -1, zip(syncBits, f))))
    for i in range(0, len(f2), 2):
        o = max(0, min((f2[i]-1) + (f2[i+1]-1)*16, 0xff))
        s += chr(o)
    try:
        return code.decode(s)[0].strip()
    except urs.rs.RSCodecError:
        return ''

#print(frame2str(str2frame('hello')))