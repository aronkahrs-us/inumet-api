# INUMET API

INUMET Api wrapper for python

## Installation

```console
$ pip install inumet_api
```

## Example
### Get all the relevant weather data
```py
# import the module
from inumet_api import INUMET

print(INUMET('Prado','Montevideo')._get_data())
```
### Get Current Conditions
```py
# import the module
from inumet_api import INUMET

print(INUMET('Prado','Montevideo').estado_actual())
```

### Get the list of stations
```py
# import the module
from inumet_api import INUMET

print(INUMET().estaciones())
```