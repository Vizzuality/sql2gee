[![license](https://img.shields.io/packagist/l/doctrine/orm.svg)](https://github.com/Vizzuality/sql2gee/blob/develop/LICENSE)
[![Build Status](https://travis-ci.org/Vizzuality/forest-atlas-landscape-cms.svg?branch=develop)](https://travis-ci.org/Vizzuality/forest-atlas-landscape-cms)
[![codecov](https://codecov.io/gh/Vizzuality/sql2gee/branch/develop/graph/badge.svg)](https://codecov.io/gh/Vizzuality/sql2gee)

# sql2gee

[Read the docs](https://vizzuality.github.io/sql2gee/)

A Python 2.7 library to make SQL-like queries to Google's Earth Engine and Fusion Tables. It is able to perform
Postgis-like operations, including returning summary statistics, and histogram data for Images, including subsetting
by geojson vector data.




### Example usage

1. Import the SQL2GEE class from the sql2gee library in python.
```python
>>>import ee
>>>from sql2gee import SQL2GEE
>>>ee.Initialize()
>>>q = SQL2GEE('select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100 ')
>>>print "Result of my query: ", q.response
Result of my query: 1919
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

### Notes

Currently, Python 3.x is not supported, due to the G.E.E python API.

### Want to Contribute?
Submit a pull request and I'll gladly review it.
