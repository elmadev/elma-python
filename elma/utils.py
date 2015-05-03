def null_padded(string, length):
    """
    Force a string to a given length by right-padding it with zero-bytes,
    clipping the initial string if neccessary.
    """
    return string[:length] + ('\0' * (length - len(string)))
