# sql2gee
> Library to do sql queries to Google Earth Engine

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
  
##GEE Supported:
* FeatureCollection
  
##Usage

Important: To use this library, the first is that you initialize the GEE library.
Example:
```python
import ee
ee.Initialize()
```


Example library usage:

1 - Import library in your python file
```python
from sql2gee.sql2gee import SQL2GEE
```

2 - Create an instance of SQL2GEE with the sql that you want execute in GEE
```python
sql2gee = SQL2GEE('select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100 ')
```
  
3 - Generate the GEE object
```python
sql2gee.generate_query()
```

4 - Execute the query in GEE Servers
```python
print "result", sql2gee.execute()
```

##Develop

Create virtualenv:
```
virtualenv env
```

Execute test:
```
make test
```


More doc in Test


## Want to Contribute?
Submit a pull request and I'll gladly review it.
