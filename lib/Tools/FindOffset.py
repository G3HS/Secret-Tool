#List of offsets locater
from binascii import hexlify, unhexlify

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
        