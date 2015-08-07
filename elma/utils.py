try:
    bytes('A', 'latin1')
except TypeError:
    bytes = lambda a, b: a
    chr = lambda a: a if type(a) == str else chr(a)


def null_padded(string, length):
    """
    Force a string to a given length by right-padding it with zero-bytes,
    clipping the initial string if neccessary.
    """
    return bytes(string[:length] + ('\0' * (length - len(string))), 'latin1')
