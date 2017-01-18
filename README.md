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

* FEATURE COLLECTION FUNCTIONS
  * COUNT
  * SUM
  * AVG
  * MAX
  * MIN
  * FIRST
  * LAST
  * LIMIT
  
* POSTGIS-LIKE IMAGE FUNCTIONS
  * ST_METADATA
  * ST_HISTOGRAM
  * ST_SUMMARYSTATS

## Currently Supported Earth Engine objects:
* FeatureCollection
* Image

##Usage

#### Feature Collection operations
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

3. Returns the result from executing the GEE query in on Google's servers.

```python
>>>print "Result of my query: ", q.response
Result of my query: 1919
```

Here is another example, showing how you can limit the responses from a feature collection.

```python
>>>sql = 'select * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT 1'
>>>q = SQL2GEE(sql)
>>>q.response
{u'columns': 
...
 u'type': u'FeatureCollection'}
```



#### Image operations 

You can use SQL2GEE to extract info from an Image resource (e.g. the SRTM Digital Elevation Data Version 4 data: [srtm90_v4](http://srtm.csi.cgiar.org)). First, load SQL2GEE and the EE library, and Initialise an Earth Engine session.
```python
>>>from sql2gee import SQL2GEE
>>>import ee
>>>ee.Initialize()
```

You can access the execute property of the SQL2GEE object directly, rather than assigning the object to a variable as in the previous example. 
Below we show how to return metadata for the image resource.

```python
>>>SQL2GEE("SELECT ST_METADATA() FROM srtm90_v4").response
-- Band 0 --
CRS:  EPSG:4326
Transform:  [0.000833333333333, 0.0, -180.0, 0.0, -0.000833333333333, 60.0]
Data type:  PixelType
ID:  elevation
Pixel Dimensions:  [432000, 144000]
Min value:  -32768
Max value:  32767
```

You can also retrieve summary statistics per band:

```python
>>>SQL2GEE("SELECT ST_SUMMARYSTATS() FROM srtm90_v4").response
Band = elevation, min = -415, mean = 689.847483377, max = 7159
```

You can also return a dictionary object of histogram data. (Note, bin numbers are set via the Freedman-Diaconis method.)
```python
>>>SQL2GEE("SELECT ST_HISTOGRAM() FROM srtm90_v4").response
{u'elevation': [[-415.0, 14.0],
  [-404.94156706507306, 6.0],
  [-394.88313413014606, 3.0],
  [-384.8247011952191, 1.0],
  ...
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
