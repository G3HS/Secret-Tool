# coding: utf-8
"""Character mapping codec for use with Pokémon games in Generation III (Ruby, Sapphire, Emerald, FireRed and LeafGreen.
"""
import codecs

class Codec(codecs.Codec):
    def encode(self, input, errors="strict"):
        return codecs.charmap_encode(input, errors, encoding_dict)
    
    def decode(self, input, errors="strict"):
        return codecs.charmap_decode(input, errors, decoding_dict)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, encoding_dict)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, decoding_dict)[0]

class StreamWriter(Codec, codecs.StreamWriter):
    pass

class StreamReader(Codec, codecs.StreamReader):
    pass

def getregentry():
    return codecs.CodecInfo(
        name="pokemon",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )

decoding_dict = {
    0x00: u' ',
    0x01: u'À',
    0x02: u'Á',
    0x03: u'Â',
    0x04: u'Ç',
    0x05: u'È',
    0x06: u'É',
    0x07: u'Ê',
    0x08: u'Ë',
    0x09: u'Ì',
    0x0A: None,
    0x0B: u'Î',
    0x0C: u'Ï',
    0x0D: u'Ò',
    0x0E: u'Ó',
    0x0F: u'Ô',
    0x10: u'Œ',
    0x11: u'Ù',
    0x12: u'Ú',
    0x13: u'Û',
    0x14: u'Ñ',
    0x15: u'ß',
    0x16: u'à',
    0x17: u'á',
    0x18: None,
    0x19: u'ç',
    0x1A: u'è',
    0x1B: u'é',
    0x1C: u'ê',
    0x1D: u'ë',
    0x1E: u'ì',
    0x1F: None,
    0x20: u'î',
    0x21: u'ï',
    0x22: u'ò',
    0x23: u'ó',
    0x24: u'ô',
    0x25: u'œ',
    0x26: u'ù',
    0x27: u'ú',
    0x28: u'û',
    0x29: u'ñ',
    0x2A: u'º',
    0x2B: u'ª',
    0x2C: u'¹',
    0x2D: u'&',
    0x2E: u'+',
    0x2F: None,
    0x30: None,
    0x31: None,
    0x32: None,
    0x33: None,
    0x34: None, # '[Lv]'
    0x35: u'=',
    0x36: u';',
    0x37: None,
    0x38: None,
    0x39: None,
    0x3A: None,
    0x3B: None,
    0x3C: None,
    0x3D: None,
    0x3E: None,
    0x3F: None,
    0x40: None,
    0x41: None,
    0x42: None,
    0x43: None,
    0x44: None,
    0x45: None,
    0x46: None,
    0x47: None,
    0x48: None,
    0x49: None,
    0x4A: None,
    0x4B: None,
    0x4C: None,
    0x4D: None,
    0x4E: None,
    0x4F: None,
    0x50: None,
    0x51: u'¿',
    0x52: u'¡',
    0x53: None, # '[PK]'
    0x54: None, # '[MN]'
    0x55: None, # '[PO]'
    0x56: None, # '[Ké]'
    0x57: None, # '[BL]'
    0x58: None, # '[OC]'
    0x59: None, # '[K]'
    0x5A: u'Í',
    0x5B: u'%',
    0x5C: u'(',
    0x5D: u')',
    0x5E: None,
    0x5F: None,
    0x60: None,
    0x61: None,
    0x62: None,
    0x63: None,
    0x64: None,
    0x65: None,
    0x66: None,
    0x67: None,
    0x68: u'â',
    0x69: None,
    0x6A: None,
    0x6B: None,
    0x6C: None,
    0x6D: None,
    0x6E: None,
    0x6F: u'í',
    0x70: None,
    0x71: None,
    0x72: None,
    0x73: None,
    0x74: None,
    0x75: None,
    0x76: None,
    0x77: None,
    0x78: None,
    0x79: None,
    0x7A: None,
    0x7B: None,
    0x7C: None,
    0x7D: None,
    0x7E: None,
    0x7F: None,
    0x80: None,
    0x81: None,
    0x82: None,
    0x83: None,
    0x84: None,
    0x85: None,
    0x86: None,
    0x87: None,
    0x88: None,
    0x89: None,
    0x8A: None,
    0x8B: None,
    0x8C: None,
    0x8D: None,
    0x8E: None,
    0x8F: None,
    0x90: None,
    0x91: None,
    0x92: None,
    0x93: None,
    0x94: None,
    0x95: None,
    0x96: None,
    0x97: None,
    0x98: None,
    0x99: None,
    0x9A: None,
    0x9B: None,
    0x9C: None,
    0x9D: None,
    0x9E: None,
    0x9F: None,
    0xA0: None,
    0xA1: u'0',
    0xA2: u'1',
    0xA3: u'2',
    0xA4: u'3',
    0xA5: u'4',
    0xA6: u'5',
    0xA7: u'6',
    0xA8: u'7',
    0xA9: u'8',
    0xAA: u'9',
    0xAB: u'!',
    0xAC: u'?',
    0xAD: u'.',
    0xAE: u'-',
    0xAF: u'|',
    0xB0: u'…',
    0xB1: u'“',
    0xB2: u'”',
    0xB3: "‘",
    0xB4: u'’',
    0xB5: u'♂',
    0xB6: u'♀',
    0xB7: u'$',
    0xB8: u',',
    0xB9: u'×',
    0xBA: u'/',
    0xBB: u'A',
    0xBC: u'B',
    0xBD: u'C',
    0xBE: u'D',
    0xBF: u'E',
    0xC0: u'F',
    0xC1: u'G',
    0xC2: u'H',
    0xC3: u'I',
    0xC4: u'J',
    0xC5: u'K',
    0xC6: u'L',
    0xC7: u'M',
    0xC8: u'N',
    0xC9: u'O',
    0xCA: u'P',
    0xCB: u'Q',
    0xCC: u'R',
    0xCD: u'S',
    0xCE: u'T',
    0xCF: u'U',
    0xD0: u'V',
    0xD1: u'W',
    0xD2: u'X',
    0xD3: u'Y',
    0xD4: u'Z',
    0xD5: u'a',
    0xD6: u'b',
    0xD7: u'c',
    0xD8: u'd',
    0xD9: u'e',
    0xDA: u'f',
    0xDB: u'g',
    0xDC: u'h',
    0xDD: u'i',
    0xDE: u'j',
    0xDF: u'k',
    0xE0: u'l',
    0xE1: u'm',
    0xE2: u'n',
    0xE3: u'o',
    0xE4: u'p',
    0xE5: u'q',
    0xE6: u'r',
    0xE7: u's',
    0xE8: u't',
    0xE9: u'u',
    0xEA: u'v',
    0xEB: u'w',
    0xEC: u'x',
    0xED: u'y',
    0xEE: u'z',
    0xEF: None,
    0xF0: u':',
    0xF1: u'Ä',
    0xF2: u'Ö',
    0xF3: u'Ü',
    0xF4: u'ä',
    0xF5: u'ö',
    0xF6: u'ü',
    0xF7: None,
    0xF8: None,
    0xF9: None,
    0xFA: None,
    0xFB: u'+',
    0xFC: None,
    0xFD: None,
    0xFE: u'\n',
    0xFF: None,
}
encoding_dict = {
    10: b'\xfe',
    32: b'\x00',
    33: b'\xab',
    36: b'\xb7',
    37: b'[',
    38: b'-',
    40: b'\\',
    41: b']',
    43: b'\xfb',
    44: b'\xb8',
    45: b'\xae',
    46: b'\xad',
    47: b'\xba',
    48: b'\xa1',
    49: b'\xa2',
    50: b'\xa3',
    51: b'\xa4',
    52: b'\xa5',
    53: b'\xa6',
    54: b'\xa7',
    55: b'\xa8',
    56: b'\xa9',
    57: b'\xaa',
    58: b'\xf0',
    59: b'6',
    61: b'5',
    63: b'\xac',
    65: b'\xbb',
    66: b'\xbc',
    67: b'\xbd',
    68: b'\xbe',
    69: b'\xbf',
    70: b'\xc0',
    71: b'\xc1',
    72: b'\xc2',
    73: b'\xc3',
    74: b'\xc4',
    75: b'\xc5',
    76: b'\xc6',
    77: b'\xc7',
    78: b'\xc8',
    79: b'\xc9',
    80: b'\xca',
    81: b'\xcb',
    82: b'\xcc',
    83: b'\xcd',
    84: b'\xce',
    85: b'\xcf',
    86: b'\xd0',
    87: b'\xd1',
    88: b'\xd2',
    89: b'\xd3',
    90: b'\xd4',
    97: b'\xd5',
    98: b'\xd6',
    99: b'\xd7',
    100: b'\xd8',
    101: b'\xd9',
    102: b'\xda',
    103: b'\xdb',
    104: b'\xdc',
    105: b'\xdd',
    106: b'\xde',
    107: b'\xdf',
    108: b'\xe0',
    109: b'\xe1',
    110: b'\xe2',
    111: b'\xe3',
    112: b'\xe4',
    113: b'\xe5',
    114: b'\xe6',
    115: b'\xe7',
    116: b'\xe8',
    117: b'\xe9',
    118: b'\xea',
    119: b'\xeb',
    120: b'\xec',
    121: b'\xed',
    122: b'\xee',
    124: b'\xaf',
    161: b'R',
    170: b'+',
    185: b',',
    186: b'*',
    191: b'Q',
    192: b'\x01',
    193: b'\x02',
    194: b'\x03',
    196: b'\xf1',
    199: b'\x04',
    200: b'\x05',
    201: b'\x06',
    202: b'\x07',
    203: b'\x08',
    204: b'\t',
    205: b'Z',
    206: b'\x0b',
    207: b'\x0c',
    209: b'\x14',
    210: b'\r',
    211: b'\x0e',
    212: b'\x0f',
    214: b'\xf2',
    215: b'\xb9',
    217: b'\x11',
    218: b'\x12',
    219: b'\x13',
    220: b'\xf3',
    223: b'\x15',
    224: b'\x16',
    225: b'\x17',
    226: b'h',
    228: b'\xf4',
    231: b'\x19',
    232: b'\x1a',
    233: b'\x1b',
    234: b'\x1c',
    235: b'\x1d',
    236: b'\x1e',
    237: b'o',
    238: b' ',
    239: b'!',
    241: b')',
    242: b'"',
    243: b'#',
    244: b'$',
    246: b'\xf5',
    249: b'&',
    250: b"'",
    251: b'(',
    252: b'\xf6',
    338: b'\x10',
    339: b'%',
    8216: b'\xb3',
    8217: b'\xb4',
    8220: b'\xb1',
    8221: b'\xb2',
    8230: b'\xb0',
    9792: b'\xb6',
    9794: b'\xb5',
}
