from binascii import hexlify, unhexlify
import wx

# Little endian
bytes_to_int = lambda b : int(hexlify(''.join(i for i in reversed(b))), 16)

def LZUncompress(rom, offset):
    """
    This function will take a byte string like "\xFF\xFF\x34\x48..." and 
    decompress it LZ77 GBA. It will return a byte string (like the one it
    accepted) and the original compressed size of the image in a tuple: (data, size).
    
    Credits to Jambo51 and Shiny Quagsire for helping me get this right!
    """
    ##Here, we read the first byte. If it isn't 0x10, then this is not LZ Compressed Data.
    rom.seek(offset)
    check = rom.read(1)
    if check != "\x10":
        return (False,False)
    ##Now, the next 3 bytes are little endian and tell the length of the uncompressed data.
    data_length = bytes_to_int(rom.read(3))
    
    uncompressed = ""
    i = 0
    while True:
        ##Load the bit field that tells what bytes are compressed and what are raw.
        bit_field = hexlify(rom.read(1))
        bit_field = bin(int(bit_field,16))[2:].zfill(8)
        ##Now uncompress bytes.
        for bit in bit_field:
            if bit == "1": #Next bytes are compressed.
                ##This code directly follows the ASM in the GBA BIOS. That is why the 
                ##variables are rX. 
                r5 = int(hexlify(rom.read(1)),16)
                store = r5
                r6 = 3
                r3 = (r5>>4)+r6
                r6 = store
                r5 = r6 & 0xF
                r12 = r5<<8
                r6 = int(hexlify(rom.read(1)),16)
                r5 = r6 | r12
                r12 = r5 +1
                for n in range(r3):
                    try: r5 = uncompressed[-r12]
                    except:
                        ERROR = wx.MessageDialog(None, 
                                "Bad LZ77 compressed data at "+hex(offset), 
                                'Error loading sprite data...', 
                                wx.OK | wx.ICON_ERROR)
                        ERROR.ShowModal()
                        return (False,False)
                    uncompressed += r5
                    if len(uncompressed) == data_length: 
                        size = rom.tell()-offset
                        return (uncompressed, size)
            elif bit == "0":
                byte = rom.read(1)
                uncompressed += byte
                if len(uncompressed) == data_length:
                    size = rom.tell()-offset
                    return (uncompressed, size)
    
def LZCompress(data):
    """
    This function will take a byte string like "\xFF\xFF\x34\x48..." and 
    compress it LZ77 GBA. It will return a byte string, like the one it
    accepted.
    
    Credits to DoesntKnowHowToPlay and Interdpth for helping me get this right!
    """
    compressed = "\x10"
    data_length = len(data)
    hex_data_length = hex(data_length)[2:].zfill(6)
    hex_data_length = unhexlify(hex_data_length)[::-1]
    compressed += hex_data_length
    
    index = 0 #Current compression position
    w = 4095 #Window Length: 0xFFF
    window = None   #This is the last 18 bytes to be compressed in the uncompressed.
    lookahead = None #This is the remaining data to be compressed.
    while True:
        bits = "" #This is the bit field that tells if data is raw or compressed.
        check = None #The index of lookahead[0:3] in window.
        currCompSet = "" #The set of bytes that have been compressed so far for this bit field.
        for n in range(8):
            if index < w: window = data[:index]
            else: window = data[index-w:index]
            lookahead = data[index:]
            if lookahead == "":
                if bits != "":
                    while len(bits) != 8:
                        bits += "0"
                        currCompSet += "\x00"
                    compressed += unhexlify(hex(int(bits,2))[2:].zfill(2))+currCompSet
                break
            check = window.find(lookahead[0:3]) #Need to find at least a 3 byte match
            if check == -1:
                index += 1
                bits += "0" #Uncompressed data
                currCompSet += lookahead[0]
            else:
                bits += "1" #Compressed data
                length = 2
                while check != -1 and length < 18:
                    store_length = length #Store the old length before we increment it.
                    length += 1
                    store_check = check #Store the old check before it gets overwritten
                    check = window.find(lookahead[0:length])
                index += store_length
                store_length -= 3 #Cut it down to GBA specifications of 4bit length.
                position = len(window)-store_check-1
                store_length = store_length << 12
                pos_and_len = hex(store_length | position)[2:].zfill(4)
                pos_and_len = unhexlify(pos_and_len)
                currCompSet += pos_and_len
        if lookahead == "":
                if bits != "":
                    while len(bits) != 8: #Make sure the bits and currCompSet are backfilled with 00s for alignment.
                        bits += "0"
                        currCompSet += "\x00"
                    compressed += unhexlify(hex(int(bits,2))[2:].zfill(2))+currCompSet
                break
        compressed += unhexlify(hex(int(bits,2))[2:].zfill(2))+currCompSet
    return compressed

