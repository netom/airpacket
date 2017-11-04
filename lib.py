import unireedsolomon as urs

code = urs.rs.RSCoder(20,10)

syncBits = [
    1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1,  1,  1, -1,  1,  1,
    1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1,  1,  1, -1,  1,  1,
    1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1, 
   -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1,  1,  1, -1,
    1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1,  1, -1,  1,
   -1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1, -1,
    1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1,
    1,  1, -1,  1, -1, -1, -1
]

symbols = list(range(17))

print(sum(syncBits))

def str2nibbles(s):
    ns = []
    for c in s:
        ns.append(ord(c) & 0x0f)
        ns.append(ord(c) >> 4)
    return ns

def str2frame(s):
    return str2nibbles(code.encode(s.rjust(10)))

def frame2str(f):
    s = ''
    for i in range(0, len(f), 2):
        s += chr(f[i] + f[i+1]*16)
    try:
        return code.decode(s)[0].strip()
    except urs.rs.RSCodecError:
        return ''
