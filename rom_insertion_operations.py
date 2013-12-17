from baseconv import *
import binascii

def get_decimal_offset_from_hex_string(string):
    offset = HEXADECIMAL(string)
    offset.base = DECIMAL
    offset = int(str(offset))
    return offset
    
def get_bytes_string_from_hex_string(string):
    if len(string) % 2 != 0:
        string = "0"+string
    return binascii.unhexlify(string)