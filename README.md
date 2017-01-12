[![Build Status](https://travis-ci.org/benlaken/sql2gee.svg?branch=master)](https://travis-ci.org/benlaken/sql2gee)

# sql2gee
A python 2.7 library to convert SQL queries into Google's Earth Engine Python API calls.

##SQL Supported:
* SELECT (only with one table, joins not supported)
* WHERE
  * \>, <, >=, <=, <>, =
  * LIKE, NOT LIKE
  * NOT
  * AND, OR
  * IN
  * IS

* FUNCTIONS
  * COUNT
  * SUM
  * AVG
  * MAX
  * MIN
  * FIRST
  * LAST

## GEE Currently Supported:
* FeatureCollection

##Usage

Important: To use this library, you must first initialize the Google Earth Engine (GEE) library (e.g. as shown below).
```python
>>>import ee
>>>ee.Initialize()
```


Example library usage:

1. Import the SQL2GEE class from the sql2gee library in python.
```python
>>>from sql2gee import SQL2GEE
```

2. Create an instance of SQL2GEE with the SQL command that you want execute in GEE, e.g. as shown below.
```python
>>>q = SQL2GEE('select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100 ')
```

3. Execute the GEE query in on Google's servers.

```python
>>>print "Result of my query: ", q.execute()
'Result of my query:', 1919
```


##Development

Create virtualenv:
```bash
$virtualenv env
```

Execute test:
```bash
$make test
```

or using py.test

```bash
$cd <path/sql2gee>
$py.test
```

More documentation can be found in the docstrings and tests.


## Notes

Currently, Python 3.x is not supported, due to the G.E.E python API.

## Want to Contribute?
Submit a pull request and I'll gladly review it.
