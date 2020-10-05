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


### Loading a level from a file
```python
from elma.packing import unpack_level

with open('mylevel.lev', 'rb') as f:
    level = unpack_level(f.read())
```


### Saving a level to a file
```python
from elma.packing import pack_level

level = ...

with open('mylevel.lev', 'wb') as f:
    f.write(pack_level(level))
```


### Merging level top10s
```python
from elma.packing import unpack_level
from elma.packing import pack_level

with open('mylevel1.lev', 'rb') as f:
    level1 = unpack_level(f.read())
with open('mylevel2.lev', 'rb') as f:
    level2 = unpack_level(f.read())

if level1 == level2:
    level1.top10.merge(level2.top10)
    with open('mylevel.lev', 'wb') as f:
        f.write(pack_level(level1))
```


### Loading a replay from a file
```python
from elma.packing import unpack_replay

with open('myreplay.rec', 'rb') as f:
    replay = unpack_replay(f.read())
```


### Saving a replay to a file
```python
from elma.packing import pack_replay

replay = ...

with open('myreplay.rec', 'wb') as f:
    f.write(pack_replay(replay))
```


## Development setup

```
virtualenv venv
. venv/bin/activate
make setup
```


## Running tests

```
make test
```


## Linting

To lint the project, do:

```
make lint
```


## Contributing

Pull requests welcome!
