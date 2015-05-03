# Elma Python Library

Elma Python Library is a python library for manipulating Elastomania files.
Currently, it supports simple level manipulation.

## Documentation

[Documentation is available at elma-python-library.readthedocs.org](https://elma-python-library.readthedocs.org).

# Usage

## Loading a level from file
```
from elma.packing import unpack

with open('mylevel.lev') as f:
    level = unpack(f.read())
```

## Saving a level to file
```
from elma.packing import pack

level = ...

with open('mylevel.lev', 'w') as f:
    f.write(pack(level))
```
