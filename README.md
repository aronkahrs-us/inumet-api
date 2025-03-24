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

print(INUMET(lat=-34.90657685747718, long=-56.199728569298955)._get_data())
```
### Get Current Conditions
```py
# import the module
from inumet_api import INUMET

print(INUMET(lat=-34.90657685747718, long=-56.199728569298955).estado_actual())
```

### Get the list of stations
```py
# import the module
from inumet_api import INUMET

print(INUMET().estaciones())
```