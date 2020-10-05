from pathlib import Path
from typing import Union

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


def check_writable_file(file: Union[str, Path], exist_ok: bool = False, create_dirs: bool = False) -> None:
    """
    Check if file can be written to and optionally create non-existing parent
    directories.

    Args:
        file: path to the file
        exist_ok: if False, FileExistsError is raised if the file already exists
        create_dirs: create non-existing parent directories of the file

    Raises:
        FileExistsError: if file exists and exist_ok = False
        FileNotFoundError: if parent directory of the file does not exists
            and create_dirs = False
    """
    file = Path(file)
    if file.exists() and not exist_ok:
        raise FileExistsError(f"File {file} already exists.")
    parent = file.resolve().parent
    if create_dirs:
        parent.mkdir(parents=True, exist_ok=True)
    elif not parent.exists():
        raise FileNotFoundError(f"Directory {parent} not found")
