[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/Vizzuality/sql2gee/blob/develop/LICENSE)
[![Build Status](https://travis-ci.org/Vizzuality/forest-atlas-landscape-cms.svg?branch=develop)](https://travis-ci.org/Vizzuality/forest-atlas-landscape-cms)
[![codecov](https://codecov.io/gh/Vizzuality/sql2gee/branch/develop/graph/badge.svg)](https://codecov.io/gh/Vizzuality/sql2gee)

# sql2gee

[Read the docs](https://vizzuality.github.io/sql2gee/)

A Python 3 library to make SQL-like queries to Google's Earth Engine Main asset data types (Feature Collections, and Fusion Tables, Image Collections and Images).  It is able to perform
Postgis-like operations, including returning summary statistics, and histogram data and subsetting by geojson vector data.




### Example usage

1. Import the SQL2GEE class from the sql2gee library in python.
```python
>>>import ee
>>>from sql2gee import SQL2GEE
>>>from utils.jsonSql import JsonSql
>>>ee.Initialize()
>>>
>>>sql = "SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'"
>>>myQuery = SQL2GEE(JsonSql(sql).to_json())
>>>print("Result of my query: ", q.response)
Result of my query: [{'ST_HISTOGRAM': {'lossyear': None}}]
```

### Execute tests

```bash
$make test
```

or using py.test

```bash
$cd <path/sql2gee>
$py.test -v
```

## Development


### Notes

### Want to Contribute?
Submit a pull request and We will review it.
