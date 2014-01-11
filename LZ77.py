from rom_insertion_operations import *

"""
Structure:
header = 0x10 [3 bytes- length of uncompressed data]
"""

def LZUncompress(rom, offset):
    ##Here, we read the first byte. If it isn't 0x10, 
    ##then this is not LZ Compressed Data.
    rom.seek(offset)
    check = rom.read(1)
    if check != "\x10":
        return "Not LZ77 Compressed."
    ##Now, the next 3 bytes are little endian and 
    ##tell the length of the uncompressed data.
    tmp = rom.read(3)
    data_length = tmp[2]+tmp[1]+tmp[0]
    data_length = get_bytes_string_from_hex_string(data_length)
    data_length = int(data_length, 16)
    
    uncompressed = ""
    i = 0
    while True:
        ##Load the bit field that tells what bytes 
        ##are compressed and what are raw.
        bit_field = get_bytes_string_from_hex_string(rom.read(1))
        bit_field = bin(int(bit_field,16))[2:].zfill(8)
        print bit_field, "|", hex(int(bit_field, 2)),"|", hex(rom.tell())
        ##Now uncompress bytes.
        for bit in bit_field:
            if bit == "1":
                r5 = int(get_bytes_string_from_hex_string(rom.read(1)),16)
                store = r5
                r6 = 3
                r3 = (r5>>4)+r6
                print "r3", hex(r3)
                r6 = store
                print "r6", hex(r6) 
                r5 = r6 & 0xF
                print "r5", hex(r5)
                r12 = r5<<8
                print "r12", hex(r12)
                r6 = int(get_bytes_string_from_hex_string(rom.read(1)),16)
                print "r6", hex(r6)
                r5 = r6 | r12
                print "r5", hex(r5)
                r12 = r5 +1
                print "r12", hex(r12)
                for n in range(r3):
                    r5 = uncompressed[-r12]
                    print "r5", get_bytes_string_from_hex_string(r5)
                    uncompressed += r5
                    if len(uncompressed) == data_length: return uncompressed
            elif bit == "0":
                byte = rom.read(1)
                uncompressed += byte
                if len(uncompressed) == data_length: return uncompressed
    
def LZCompress(data):
    ##Data is a string of byte values like "\xFF".
    compressed = "\x10"
    data_length = len(data)
    hex_data_length = hex(data_length)[2:].zfill(6)
    hex_data_length = get_hex_from_string(hex_data_length)[::-1]
    compressed += hex_data_length
    
    while True:
        bits = ""
        current_string = ""
        for n in range(8):
            if data == "":
                current_string += "\x00"
                bits += "0"
                continue
            else: byte = data[0]
            x = 0
            if data[1] == byte:
                while tmp == byte and x < 0xFF:
                    x += 1
                    try: tmp = data[x]
                    except: break
                multiplier = x
                bits += 1
                current_string += multiplier
                current_string += byte
                data = data[x:]
            else:
                bits += 0
                current_string += byte
                data = data[1:]
        bits = bits[::-1]
        bit_field = hex(int(bits, 2))[2:]
        bit_field = get_hex_from_string(bit_field)
        compressed += bit_field
        compressed += current_string
    return compressed
        
    
    
                
                
                
                