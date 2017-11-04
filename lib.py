import unireedsolomon as urs

RATE   = 44100
BUFFER = 100

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

code = urs.rs.RSCoder(54, 34) # 20 payload bytes, 34 additional bytes

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
    raw = str2nibbles(code.encode(s.rjust(20)))
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

#print(nibbles2str(nubsync(str2frame('Hello World!'))))
