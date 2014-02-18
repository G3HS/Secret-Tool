#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from baseconv import *
import binascii
import string as st
import re
import platform
from Encoding import *

def encode_per_platform(string):
    p = platform.system()
    if p == "Windows": out = string #.decode('Latin-1').encode('utf-8')
    else: out = string.decode('Latin-1').encode('utf-8')
    return out

def deal_with_16bit_signed_hex(hex_value, method="forward"):
    """
    This function, will take a hex value and check if it is signed and then
    return its int value.
    If the given value is already an int, it will convert it back and
    return a signed hex value.
    
    Valid methods are:
    
    "forward": Signed Hex -> Int
    
    "backward": Int -> Signed Hex
    """
    if method == "forward":
        binary = bin(hex_value)[2:].zfill(16)
        if binary[0] == "1":
            x = int(binary, 2)
            output = x-0x10000
        else: 
            output = int(binary, 2)
        return output
    elif method == "backward":
        if hex_value < 0:
            output = hex_value+0x10000 
            output = hex(output)[2:].zfill(4)
        else: output = hex(hex_value)[2:].zfill(4)
        return output
    else: return None
    
def deal_with_8bit_signed_hex(hex_value, method="forward"):
    """
    This function, will take a hex value and check if it is signed and then
    return its int value.
    If the given value is already an int, it will convert it back and
    return a signed hex value.
    
    Valid methods are:
    
    "forward": Signed Hex -> Int
    
    "backward": Int -> Signed Hex
    """
    if method == "forward":
        binary = bin(hex_value)[2:].zfill(16)
        if binary[0] == "1":
            x = int(binary, 2)
            output = x-0x100
        else: 
            output = int(binary, 2)
        return output
    elif method == "backward":
        if hex_value < 0:
            output = hex_value+0x100 
            output = hex(output)[2:].zfill(4)
        else: output = hex(hex_value)[2:].zfill(4)
        return output
    else: return None

def get_decimal_offset_from_hex_string(string):
    offset = HEXADECIMAL(string)
    offset.base = DECIMAL
    offset = int(str(offset))
    return offset
    
def get_hex_from_string(string):
    """
    Take a hex string like "00FF58" and convert it to a UTF-8 string.
    """
    if len(string) % 2 != 0:
        string = "0"+string
    try: return binascii.unhexlify(string)
    except:
        return None
    
def get_bytes_string_from_hex_string(string):
    """
    Take a UTF-8 string and convert it to a hex string.
    """
    return binascii.hexlify(string)

def split_string_into_bytes(string):
    if len(string)%2 != 0:
        string = "0"+string
    list_of_bytes = re.findall('..',string)
    return list_of_bytes
    
def insert_string_of_bytes_into_rom(offset, rom, string):
    offset = get_decimal_offset_from_hex_string(offset)
    rom.seek(offset, 0)
    rom.write(string)
    return
    
def generate_list_of_names(offset, datalength, terminating_character, num_of_names, rom):
    rom.seek(offset)
    list_of_names = []
    for n in range(num_of_names):
        rom.seek(offset+n*datalength)
        tmp = rom.read(datalength)
        tmp = tmp.split(terminating_character, 1)
        tmp = convert_ascii_and_poke(tmp[0], "to_poke")
        list_of_names.append(tmp)
    return list_of_names    

def read_pointer(string):
    #take a pointer in utf-8 reversed format (fresh rom read) and return int offset.
    bytes = get_bytes_string_from_hex_string(string)
    list_of_bytes = split_string_into_bytes(bytes)
    list_of_bytes = reversed(list_of_bytes)
    offset = ""
    for byte in list_of_bytes:
        offset += byte
    offset = offset[2:]
    return int(offset, 16)
    
def make_pointer(string):
    #make a pointer in XXYYZZ08 format from 08ZZYYXX.
    list_of_bytes = split_string_into_bytes(string)
    list_of_bytes = reversed(list_of_bytes)
    offset = ""
    for byte in list_of_bytes:
        offset += byte
    return offset

def MakeByteStringPointer(offset):
    """
    Take an offset and return a rom pointer that can be inserted.
    """
    Pointer = hex(offset+0x8000000).rstrip("L").lstrip("0x").zfill(8)
    Pointer = make_pointer(Pointer)
    Pointer = binascii.unhexlify(Pointer)
    return Pointer
    
def reverse_hex(string):
    list_of_bytes = split_string_into_bytes(string)
    list_of_bytes = reversed(list_of_bytes)
    offset = ""
    for byte in list_of_bytes:
        offset += byte
    return offset
    
def convert_ascii_and_poke(string, mode):
    #modes: "to_poke" and "to_ascii"
    chart = ENCODING
    
    if mode == "to_ascii":
        string = string.encode('Latin-1')
        old_chart = chart
        chart = {}
        for hexer, poke in old_chart:
            poke = poke.decode('Latin-1').encode('Latin-1')
            chart[poke] = hexer
        new_string = ""
        while string != "":
            char = string[0]
            current_place = 0
            if char == "[":
                x = None
                while x != "]":
                    current_place += 1
                    x = string[current_place]
                char = string[0:current_place+1]
            if len(string) > 1:
                string = string[current_place+1:]
            else:
                string = ""
            try: new = chart[char]
            except: 
                new = ""
                print "There was an error reading:", char
            new_string += new
        string = new_string
        string = re.sub("(\\\\x)", "", string, 0, re.DOTALL)
        string = binascii.unhexlify(string)
    elif mode == "to_poke":
        string = binascii.hexlify(string)
        string = string.upper()
        string = "\\x"+re.sub("((.|\n|\r){2})", "\\1\\x", string, 0)[:-2]
        for k,v in chart:
            string = string.replace(k,v)
        p = platform.system()
        if p == "Windows": string = string.decode('utf-8').encode('Latin-1')
        else: string = string.decode('Latin-1').encode('Latin-1')
        
    else: return None
    return string
    
    
