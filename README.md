# Elma Python Library

Elma Python Library is a python library for manipulating Elastomania files.
Currently, it supports simple level manipulation.

## Documentation

[Documentation is available at elma-python-library.readthedocs.org](https://elma-python-library.readthedocs.org).

## Installation

```
pip install elma
```

## Usage

### Creating a simple level
```
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



### Loading a level from file
```
from elma.packing import unpack

with open('mylevel.lev') as f:
    level = unpack(f.read())
```

### Saving a level to file
```
from elma.packing import pack

level = ...

with open('mylevel.lev', 'w') as f:
    f.write(pack(level))
```

## Contributing

Pull requests welcome!
