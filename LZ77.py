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
    
    while len(uncompressed) < data_length:
        ##Load the bit field that tells what bytes 
        ##are compressed and what are raw.
        bit_field = get_bytes_string_from_hex_string(rom.read(1))
        bit_field = bin(int(bit_field,16))[2:]
        bit_field = bit_field[::-1]
        ##Now uncompress bytes.
        for bit in bit_field:
            if bit == "1":
                multiplier = int(get_bytes_string_from_hex_string(rom.read(1)),16)
                byte = rom.read(1)
                for n in range(multiplier):
                    uncompressed += byte
            if bit == "0":
                uncompressed += rom.read(1)
    return uncompressed
    
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
                    x++
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
        
    
    
                
                
                
                