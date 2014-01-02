#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from baseconv import *
import binascii
import string as st
import re
import platform


def encode_per_platform(string):
    p = platform.system()
    if p == "Windows": out = string #.decode('Latin-1').encode('utf-8')
    else: out = string.decode('utf-8').encode('utf-8')
    return out

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
    except: print "Error on string =",string
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
        tmp = rom.read(datalength)
        tmp = tmp.split(terminating_character, 1)
        tmp = convert_ascii_and_poke(tmp[0], "to_poke")
        list_of_names.append(tmp)
    return list_of_names    

def read_pointer(string):
    #take a pointer in XXYYZZ08 format and return int offset.
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
    
def reverse_hex(string):
    list_of_bytes = split_string_into_bytes(string)
    list_of_bytes = reversed(list_of_bytes)
    offset = ""
    for byte in list_of_bytes:
        offset += byte
    return offset
    
def convert_ascii_and_poke(string, mode):
    #modes: "to_poke" and "to_ascii"
    chart = [("\\xB5",'[MALE]'),("\\xB6",'[FEMALE]'),("\\x34",'[Lv]'),("\\x53",'[PK]'),
        ("\\x54",'[MN]'),("\\x55",'[PO]'),("\\x56",'[Ké]'),("\\x57",'[BL]'),("\\x58",'[OC]'),("\\x59",'[K]'),
        ("\\xEC",'x'),("\\x00",' '),("\\x01",'À'),("\\x02",'Á'),("\\x03",'Â'),("\\x04",'Ç'),
        ("\\x05",'È'),("\\x06",'É'),("\\x07",'Ê'),("\\x08",'Ë'),("\\x09",'Ì'),("\\x0A",'\\x0A'),("\\x0B",'Î'),("\\x0C",'Ï'),("\\x0D",'Ò'),("\\x0E",'Ó'),
        ("\\x0F",'Ô'),("\\x10",'Œ'),("\\x11",'Ù'),("\\x12",'Ú'),("\\x13",'Û'),("\\x14",'Ñ'),("\\x15",'ß'),("\\x16",'à'),("\\x17",'á'),("\\x18",'\\x18'),
        ("\\x19",'Ç'),("\\x1A",'è'),("\\x1B",'é'),("\\x1C",'ê'),("\\x1D",'ë'),("\\x1E",'ì'),("\\x1F",'\\x1F'),("\\x20",'î'),("\\x21",'ï'),("\\x22",'ò'),
        ("\\x23",'ó'),("\\x24",'ô'),("\\x25",'œ'),("\\x26",'ù'),("\\x27",'ú'),("\\x28",'û'),("\\x29",'ñ'),("\\x2A",'º'),("\\x2B",'ª'),("\\x2C",'¹'),
        ("\\x2D",'&'),("\\x2F",'\\x2F'),("\\x30",'\\x30'),("\\x31",'\\x31'),("\\x32",'\\x32'),("\\x33",'\\x33'),("\\x35",'='),
        ("\\x36",';'),("\\x37",'\\x37'),("\\x38",'\\x38'), ("\\x39",'\\x39'),("\\x3A",'\\x3A'),("\\x3B",'\\x3B'),("\\x3C",'\\x3C'),
        ("\\x3D",'\\x3D'),("\\x3E",'\\x3E'),("\\x3F",'\\x3F'),("\\x40",'\\x40'),("\\x41",'\\x41'),("\\x42",'\\x42'),
        ("\\x43",'\\x43'),("\\x44",'\\x44'),("\\x45",'\\x45'),("\\x46",'\\x46'),("\\x47",'\\x47'),("\\x48",'\\x48'),("\\x49",'\\x49'),("\\x4A",'\\x4A'),
        ("\\x4B",'\\x4B'),("\\x4C",'\\x4C'),
        ("\\x4D",'\\x4D'),("\\x4E",'\\x4E'),("\\x4F",'\\x4F'),("\\x50",'\\x50'),("\\x51",'¿'),("\\x52",'¡'),("\\x5A",'Í'),("\\x5B",'%'),("\\x5C",'('),("\\x5D",')'),
        ("\\x5E",'\\x5E'),("\\x5F",'\\x5F'),("\\x60",'\\x60'),("\\x61",'\\x61'),("\\x62",'\\x62'),("\\x63",'\\x63'),("\\x64",'\\x64'),("\\x65",'\\x65'),("\\x66",'\\x66'),("\\x67",'\\x67'),
        ("\\x68",'â'),("\\x69",'?'),("\\x6A",'?'),("\\x6B",'?'),("\\x6C",'?'),("\\x6D",'?'),("\\x6E",'?'),("\\x6F",'í'),("\\x70",'?'),("\\x71",'?'),
        ("\\x72",'?'),("\\x73",'?'),("\\x74",'?'),("\\x75",'?'),("\\x76",'?'),("\\x77",'?'),("\\x78",'?'),("\\x79",'?'),("\\x7A",'?'),("\\x7B",'?'),
        ("\\x7C",'?'),("\\x7D",'?'),("\\x7E",'?'),("\\x7F",'?'),("\\x80",'?'),("\\x81",'?'),("\\x82",'?'),("\\x83",'?'),("\\x84",'?'),("\\x85",'?'),
        ("\\x86",'?'),("\\x87",'?'),("\\x88",'?'),("\\x89",'?'),("\\x8A",'?'),("\\x8B",'?'),("\\x8C",'?'),("\\x8D",'?'),("\\x8E",'?'),("\\x8F",'?'),
        ("\\x90",'?'),("\\x91",'?'),("\\x92",'?'),("\\x93",'?'),("\\x94",'?'),("\\x95",'?'),("\\x96",'?'),("\\x97",'?'),("\\x98",'?'),("\\x99",'?'),
        ("\\x9A",'?'),("\\x9B",'?'),("\\x9C",'?'),("\\x9D",'?'),("\\x9E",'?'),("\\x9F",'?'),("\\xA0",'?'),("\\xA1",'0'),("\\xA2",'1'),("\\xA3",'2'),
        ("\\xA4",'3'),("\\xA5",'4'),("\\xA6",'5'),("\\xA7",'6'),("\\xA8",'7'),("\\xA9",'8'),("\\xAA",'9'),("\\xAB",'!'),("\\xAC",'?'),("\\xAD",'.'),
        ("\\xAE",'-'),("\\xAF",'?'),("\\xB0",'..'),("\\xB1",'“'),("\\xB2",'”'),("\\xB3",'‘'),("\\xB4",'\''),("\\xB7",'$'),
        ("\\xB8",','),("\\xB9",'×'),("\\xBA",'/'),("\\xBB",'A'),("\\xBC",'B'),("\\xBD",'C'),("\\xBE",'D'),("\\xBF",'E'),("\\xC0",'F'),("\\xC1",'G'),
        ("\\xC2",'H'),("\\xC3",'I'),("\\xC4",'J'),("\\xC5",'K'),("\\xC6",'L'),("\\xC7",'M'),("\\xC8",'N'),("\\xC9",'O'),("\\xCA",'P'),
        ("\\xCB",'Q'),("\\xCC",'R'),("\\xCD",'S'),("\\xCE",'T'),("\\xCF",'U'),("\\xD0",'V'),("\\xD1",'W'),("\\xD2",'X'),("\\xD3",'Y'),
        ("\\xD4",'Z'),("\\xD5",'a'),("\\xD6",'b'),("\\xD7",'c'),("\\xD8",'d'),("\\xD9",'e'),("\\xDA",'f'),("\\xDB",'g'),("\\xDC",'h'),("\\xDD",'i'),
        ("\\xDE",'j'),("\\xDF",'k'),("\\xE0",'l'),("\\xE1",'m'),("\\xE2",'n'),("\\xE3",'o'),("\\xE4",'p'),("\\xE5",'q'),("\\xE6",'r'),("\\xE7",'s'),
        ("\\xE8",'t'),("\\xE9",'u'),("\\xEA",'v'),("\\xEB",'w'),("\\xED",'y'),("\\xEE",'z'),("\\xEF",'?'),("\\xF0",':'),("\\xF1",'Ä'),
        ("\\xF2",'Ö'),("\\xF3",'Ü'),("\\xF4",'ä'),("\\xF5",'ö'),("\\xF6",'ü'),("\\xFB",'+'),("\\xFE",'\n'),("\\x2E",'+'),("\\xF7",'?'),("\\xF8",'?'),("\\xF9",'?'),("\\xFA",'?')]
    
    
    if mode == "to_ascii":
        old_chart = chart
        chart = {}
        for hexer, poke in old_chart:
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
            except: new = ""
            new_string += new
        string = new_string
        string = re.sub("(\\\\x)", "", string, 0, re.DOTALL)
        string = binascii.unhexlify(string)
    elif mode == "to_poke":
        string = binascii.hexlify(string)
        string = string.upper()
        string = "\\x"+re.sub("(.{2})", "\\1\\x", string, 0, re.DOTALL)[:-2]
        for k,v in chart:
            string = string.replace(k,v)
        string = string.decode('iso-8859-1').encode('utf-8')
            
    else: return None
    
    return string
    
    
