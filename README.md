# Elma Python Library

[![Travis](https://img.shields.io/travis/sigvef/elma.svg)](https://travis-ci.org/sigvef/elma/)
[![PyPI](https://img.shields.io/pypi/v/elma.svg)](https://pypi.python.org/pypi/elma/)
![Licence](https://img.shields.io/pypi/l/elma.svg)

Elma Python Library is a python library for manipulating Elastomania files.
Currently, it supports simple level and replay manipulation.

## Documentation

[Documentation is available at elma-python-library.readthedocs.org](https://elma-python-library.readthedocs.org).

## Installation

```
pip install elma
```

## Usage

### Creating a simple level
```python
from elma.models import Level
from elma.models import Obj
from elma.models import Picture
from elma.models import Point
from elma.models import Polygon


level = Level()
level.name = 'My first level'
level.polygons = [
    Polygon([Point(-10, -10),
             Point(10, -10),
             Point(10, 10),
             Point(-10, 10)]),
]
level.objects = [
    Obj(Point(0, 0), Obj.START),
    Obj(Point(0, 10), Obj.FOOD, gravity=Obj.GRAVITY_UP),
    Obj(Point(0, 0), Obj.FLOWER),
]
level.pictures = [
    Picture(Point(2, 8), picture_name='flag'),
]
```

The above snippet defines a simple level that looks like this:

![](http://i.imgur.com/cl8SJgk.png)


### Loading a level from file
```python
from elma.packing import unpack

with open('mylevel.lev') as f:
    level = unpack(f.read())
```

### Saving a level to file
```python
from elma.packing import pack

level = ...

with open('mylevel.lev', 'w') as f:
    f.write(pack(level))
```

## Development setup

```
virtualenv venv
. venv/bin/acivate
make setup
```

## Running tests

```
python -m unittest
make test
```

## Linting

To lint the project, do:

```
make lint
```

## Contributing

Pull requests welcome!
