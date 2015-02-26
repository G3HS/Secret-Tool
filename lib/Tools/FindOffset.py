#List of offsets locater
from binascii import hexlify, unhexlify
from GLOBALS import *
from lib.Tools.rom_insertion_operations import *
import ConfigParser, os
import string

#from lib.Tools.FindOffset import *
#FillOutRecoveryIniPerRom("/home/roger/Documents/Pokemon Fire Red_clean.gba")

def FindOffset(offset, rom_name):
    with open(rom_name, "rb") as rom:
        read = rom.read()
    search = hex(offset).rstrip("L").lstrip("0x").zfill(8)
    search = unhexlify(search)[::-1]
    OFFSETS = []
    start = 0
    while True:
        offset = read.find(search, start)
        if offset == -1:
            break
        OFFSETS.append(offset)
        start = offset+len(search)
    with open("offsets.txt", "w+") as dump:
        dump.write("[")
        for offset in OFFSETS:
            dump.write(hex(offset)+",")
        dump.write("]")

def Search(offset, rom, length):
    with open(rom, "rb") as rom:
        read = rom.read()
    integer = offset
    OFFSETS = []
    start = 0
    search = hex(integer).rstrip("L").lstrip("0x").zfill(8)
    search = unhexlify(search)[::-1]
    for n in range(length):
        while True:
            offset = read.find(search, start)
            if offset == -1:
                break
            if offset%4 != 0:
                start = offset+1
                continue
            OFFSETS.append(offset)
            start = offset+len(search)
        integer += 1
        search = hex(integer).rstrip("L").lstrip("0x").zfill(8)
        search = unhexlify(search)[::-1]
    with open("offsets.txt", "w+") as dump:
        dump.write("[")
        for offset in OFFSETS:
            dump.write(hex(offset)+",")
        dump.write("]")

def FillOutRecoveryIniPerRom(rom):
    Globals.INI = ConfigParser.ConfigParser()
    ini = os.path.join("/media","Storage","Secret-Tool","PokeRoms.ini")
    print ini
    Globals.INI.read(ini)
    with open("dump.txt", "w+") as dump:
        CleanRoms = os.path.join("/media","Storage","Dropbox","CleanRoms")
        for rom in os.listdir(CleanRoms):
            print rom
            with open(os.path.join(CleanRoms,rom), "rb") as rom:
                read = rom.read()
            game_code = read[0xAC:0xB0]
            options = Globals.INI.options(game_code)
            tmp_ini = []
            for opt in options:
                tmp_ini.append((opt, Globals.INI.get(game_code, opt)))
            
            dump.write(game_code+" = {\n")
            for opt, value in tmp_ini:
                if value[:2] == "0x" and len(value) > 5 and "," not in value:
                    loc = int(value, 16)
                    pointer = MakeByteStringPointer(loc)
                    offset = string.find(read, pointer)
                    if offset < 0xFFF:
                        offset = string.find(read, pointer, offset+4)
                    if offset != -1:
                        dump.write("'"+opt+"': "+hex(offset).rstrip("L")+",\n")
                    else:
                        print "Opt "+opt+" failed."
            dump.write("}\n\n")
        
