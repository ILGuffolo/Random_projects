'''
#series of function and small tests with various unicode encription methods

ord() - char -> code
chr() - code -> char

### !!! returns string !!! ###
hex() - any => hex
bin() - any => bin
oct() - any => oct

### use int() instead ###

int(number, base) - int/str => dec (base = 0 for autodetecting prefixes)

0x - hex prefix
0o - oct prefix
0b - bin prefix


for "string" use:

f'{var:nmb}
n = number to replace with
m = minimum number of digits
b = base to convert in


0x0000 - 0xFFFF => basic multilingual plane (BMP)

0x010000 - 0x10FFFF => supplementary planes
'''

def unicode_info(char):
    code = ord(char)
    print( f"  Character: {char}\n  Dec: {code}\n  Hex: U+{code:04X}\n  Bin: {code:b}\n")

def bin_Transformation(char): return f'{ord(char):b}'

def encoding_info(val):
    print("\n------------------------------------------------")
    v = bin_Transformation(val)
    unicode_info(val)
    
    if len(v) <= 16: #viable for UCS-2
        UCS_v = f'{int(v, 2):016b}'
        print(f"  UCS-2\n  B-Endian: {UCS_v[:8]}-{UCS_v[8:]}\n  L-Endian: {UCS_v[8:]}-{UCS_v[:8]}\n")
    else:
        print("  UCS-2 NOT codificable (supplementary plane)\n")
        
    #UTF-8
    if len(v) <= 7:
        UTF_v = f"{int(v, 2):07b}"
        print(f"  UTF-8 1B:\n  0{UTF_v}")
    elif len(v) <= 11:
        UTF_v = f"{int(v, 2):011b}"
        print(f"  UTF-8 2B:\n  110{UTF_v[:5]}-10{UTF_v[5:]}")
    elif len(v) <= 16:
        UTF_v = f"{int(v, 2):016b}"
        print(f"  UTF-8 3B:\n  1110{UTF_v[:4]}-10{UTF_v[4:10]}-10{UTF_v[10:]}")
    elif len(v) <= 21:
        UTF_v = f"{int(v, 2):021b}"
        print(f"  UTF-8 4B:\n  11110{UTF_v[:3]}-10{UTF_v[3:9]}-10{UTF_v[9:15]}-10{UTF_v[15:]}")
    else:
        print("  UTF-8 NOT codificable (Unknown error)\n")
        
    print("------------------------------------------------")

encoding_info('f')
encoding_info('😀')



