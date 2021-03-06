[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/Vizzuality/sql2gee/blob/develop/LICENSE)
[![Build Status](https://travis-ci.org/Vizzuality/sql2gee.svg?branch=develop)](https://travis-ci.org/Vizzuality/sql2gee)
[![codecov](https://codecov.io/gh/Vizzuality/sql2gee/branch/develop/graph/badge.svg)](https://codecov.io/gh/Vizzuality/sql2gee)

# sql2gee

[Read the docs](https://vizzuality.github.io/sql2gee/)

A Python 3 library to make SQL-like queries to Google's Earth Engine Main asset data types (Feature Collections, and Fusion Tables, Image Collections and Images).  It is able to perform
Postgis-like operations, including returning summary statistics, and histogram data and subsetting by geojson vector data.


### Example usage

1. Import the SQL2GEE class from the sql2gee library in python.

```python
import ee
from sql2gee import SQL2GEE
from utils.jsonSql import JsonSql
ee.Initialize()

sql = "SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'"
query = SQL2GEE(JsonSql(sql).to_json())
print("Result of my query: ", query.response())
```

```
Result of my query: [{'st_histogram': {'lossyear': [[0.0, 6929647.301960737], [1.0, 0.0], [2.0, 3.0], [3.0, 1.0], [4.0, 13.0], [5.0, 5.0], [6.0, 5.250980392156863], [7.0, 1.0], [8.0, 5.0], [9.0, 9.0], [10.0, 12.0], [11.0, 3.0], [12.0, 6.0], [13.0, 1.0], [14.0, 16.0]]}}]
```

### Execute tests

Test run queries on GEE servers, so you need a GCP service account with access to GEE. Specifically, you need:

- The service account name (a string formatted like `<name>@<project>.iam.gserviceaccount.com`) that has permissions to access GEE.
- A JSON access key for that account.

The account name needs to be set as the `EE_ACCOUNT` environment variable. 
The JSON account key needs to be saved as a `privatekey.json` file at the root of the project.

Once both values are set, you can run the tests using tox: 

```bash
tox
```

## Development


### Notes

### Want to Contribute?

Submit a pull request and we will review it.
