try:
    bytes('A', 'latin1')
except TypeError:
    bytes = lambda a, b: a  # noqa
    chr = lambda a: a if type(a) == str else chr(a)  # noqa


def null_padded(string, length):
    """
    Force a string to a given length by right-padding it with zero-bytes,
    clipping the initial string if necessary.
    """
    return bytes(string[:length] + ('\0' * (length - len(string))), 'latin1')


def signed_mod(a, b):
    """
    Signed modulo operation for level top10 encryption/decryption.
    """
    a = a & 0xFFFF
    r = a % b
    if a > 0x7FFF:
        return -b + (r - 0x10000) % b
    return r


def crypt_top10(buffer):
    """
    Encrypt or decrypt the raw top10 buffer containing both
    singleplayer and multiplayer top10s.
    """
    # Adapted from https://github.com/domi-id/across
    top10 = [b for b in buffer]
    a, b, c, d = [21, 9783, 3389, 31]
    top10[0] ^= a
    x = (b + a * c) * d + c
    for i in range(1, len(top10)):
        top10[i] ^= (x & 0xFF)
        x += signed_mod(x, c) * c * d
    return b''.join([bytes(chr(c), 'latin1') for c in top10])
