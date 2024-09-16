import sys
import socket 
import threading

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)
print(f'[debug] HEX_FILTER={HEX_FILTER}')


def hexdump(src, length=16, show=True):
    """
    Will hexdump a string src or byte src.
    :param length:  the length must be specified or it's by-default 16.
    :param show:    

    """
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    # loop that jumps i by length, Just like every loop -> i = i+length
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        # translate each character in word to the HEX_FILTER which is ASCII representation of 256bits.
        printable = word.translate(HEX_FILTER)
        # ?
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        # ?
        hexwidth = length*3
        # ?
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results