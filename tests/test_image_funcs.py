from __future__ import print_function, division
import numpy as np
import pytest
import requests
import sys
from sql2gee import SQL2GEE
import ee

# Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    # Else, assume you have an EE_private_key environment variable with authorisation, as on Travis-CI
    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
    ee.Initialize(credentials, 'https://earthengine.googleapis.com')

def test_count_table_query():
    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 1919, "BASIC COUNT query incorrect"
    return

def test_count_table_query_with_where_statement():
    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 400'
    q = SQL2GEE(sql)
    assert q.response == 1677, "COUNT with WHERE query incorrect"
    return

def test_max_table_query():
    sql = 'select MAX(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 500.0, "Basic MAX query incorrect"
    return

def test_min_table_query():
    sql = 'select MIN(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 125.0, "Basic MIN query incorrect"
    return

def test_sum_table_query():
    sql = 'select SUM(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 924091.0, "Basic SUM query incorrect"
    return

def test_sum_with_where_table_query():
    sql = 'select SUM(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 400'
    q = SQL2GEE(sql)
    assert q.response == 83306.0, "SUM with WHERE query incorrect"
    return

def test_avg_with_where_table_query():
    sql = 'select AVG(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 400'
    q = SQL2GEE(sql)
    assert q.response == 354.4936170212766, "AVG with WHERE query incorrect"
    return

def test_avg_with_doublewhere_table_query():
    sql = 'select AVG(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100 and where width < 280'
    q = SQL2GEE(sql)
    assert q.response == 212.25, "Complex AVG (with compound WHERE) query incorrect"
    return

def test_first_table_query():
    sql = 'select FIRST(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 500.0, "Simple FIRST query incorrect"
    return

def test_first_with_where_table_query():
    sql = 'select FIRST(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 500'
    q = SQL2GEE(sql)
    assert q.response == 125.0, "FIRST with WHERE query incorrect"
    return

def test_var_table_query():
    sql = 'select VAR(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 2423.5074511457533, "Simple VAR query incorrect"

def test_var_table_where_all_equal():
    sql = 'select VAR(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width = 500'
    q = SQL2GEE(sql)
    assert q.response == 0.0, "Simple VAR query incorrect"

def test_stdev_table():
    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    q = SQL2GEE(sql)
    assert q.response == 49.22913213886421, "Simple STDEV query incorrect"

def test_stdev_width_lt_table():
    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width < 500'
    q = SQL2GEE(sql)
    assert q.response == 35.01078172011275, "STDEV with WHERE LT 500 query incorrect"

def test_stdev_width_eq_table():
    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width = 500'
    q = SQL2GEE(sql)
    assert q.response == 0.0, "STDEV with WHERE EQ 500 query incorrect"


def test_identify_band_names():
    sql = "SELECT ST_HISTOGRAM() FROM srtm90_v4"
    q = SQL2GEE(sql)
    assert q._band_names == ['elevation']
    return

def test_retrieve_image_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_METADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
    """
    q = SQL2GEE("SELECT ST_METADATA(*) FROM srtm90_v4")
    ee_meta = {u'bands': [{u'crs': u'EPSG:4326',
                           u'crs_transform': [0.000833333333333,
                                              0.0,
                                              -180.0,
                                              0.0,
                                              -0.000833333333333,
                                              60.0],
                           u'data_type': {u'max': 32767,
                                          u'min': -32768,
                                          u'precision': u'int',
                                          u'type': u'PixelType'},
                           u'dimensions': [432000, 144000],
                           u'id': u'elevation'}],
               u'id': u'srtm90_v4',
               u'properties': {u'system:asset_size': 18827626666,
                               u'system:time_end': 951177600000,
                               u'system:time_start': 950227200000},
               u'type': u'Image',
               u'version': 1463778555689000}
    assert q.response == ee_meta, 'Metadata response was not equal to expected metadata'
    return

def test_ST_HISTOGRAM():
    """Test that a dictionary containing a list of expected length and values is returned"""
    sql = "SELECT ST_HISTOGRAM() FROM srtm90_v4"
    q = SQL2GEE(sql)
    num_bins = len(q.histogram['elevation'])
    assert num_bins == 753, "Should be 753 bins by default (set by Freedman-Diaconis method)"
    assert q.response['elevation'][0] == [-415.0, 14.0], 'First bin incorrect'
    assert q.response['elevation'][-1] == [7148.941567065073, 0.0], 'Last bin incorrect'
    return

def test_ST_HISTORGRAM_multiband_image():
    expected_keys = [u'B10', u'BQA', u'B11', u'B4', u'B5', u'B6', u'B7', u'B1', u'B2', u'B3', u'B8', u'B9']
    q = SQL2GEE("SELECT ST_HISTOGRAM() FROM LC81412332013146LGN00")
    assert isinstance(q.response, dict), "Dictionary was not returned as a response"
    assert len(q.response) == 12, "Size of the dictionary was diffrent from expected response"
    assert q.response.keys() == expected_keys, "Expected keys in response dictionary were not returned"
    for key in q.response.keys():
        if q.response[key] != None:
            assert len(q.response[key]) == 210, "Expected 210 bins in histogram"
    return


def test_ST_HISTOGRAM_with_area_restriction():
    """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
    This should then be used to subset the area considered for results."""
    # Get a test geojson object by accessing Vizzuality's geostore
    gstore = "http://staging-api.globalforestwatch.org/geostore/4531cca6a8ddcf01bccf302b3dd7ae3f"
    r = requests.get(gstore)
    j = r.json()
    j = j.get('data').get('attributes').get('geojson')
    # Initilise an SQL2GEE query object with geojson
    q = SQL2GEE("SELECT ST_HISTOGRAM() FROM srtm90_v4", geojson=j)
    assert isinstance(q.geojson, ee.FeatureCollection), "Geojson data not converted to ee.FeatureCollection type"
    assert len(q.response['elevation']) == 101, "Returned area-restricted histogram not equal to len of expected result"
    flist = [freq for x, freq in q.response['elevation']]
    assert np.mean(flist) == 1168.6435643564357, "Values returned from histogram dont match expected"
    assert q.response['elevation'][0] == [126.0, 8.0], "Returned bins don't match expected values"
    return


def test_limit_on_tables():
    """Test ability to limit the size of SQL table requests"""
    sql = 'select width from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT '
    err = 'Response was not equal to size of LIMIT'
    limit = 1
    q = SQL2GEE(sql + str(limit))
    assert len(q.response['features']) == limit, err
    limit = 2
    q = SQL2GEE(sql + str(limit))
    assert len(q.response['features']) == limit, err
    limit = 5
    q = SQL2GEE(sql + str(limit))
    assert len(q.response['features']) == limit, err
    return

def test_STSUMMARYSTATS():
    """Check an expected dictionary is returned via the ST_SUMMARYSTATS() keyword"""
    expected = {u'elevation': {'count': 2747198,
                                'max': 7159,
                                'mean': 689.8474833769903,
                                'min': -415,
                                'stdev': 865.9582784994756,
                                'sum': 1859471136.0274282}}
    sql = "SELECT ST_SUMMARYSTATS() FROM srtm90_v4"
    q = SQL2GEE(sql)
    q.response == expected, "Summary stats did not match expected result"
    return

def test_STSUMMARYSTATS_with_area_restriction_from_geojson_polygon():
    """First, I need to construct a simple polygon out of multipolygon data, and pass that to SQL2GEE"""
    expected = {u'elevation': {'count': 99626,
                               'max': 489,
                               'mean': 345.39571999277297,
                               'min': 194,
                               'stdev': 64.2380798454734,
                               'sum': 34410394.0}}
    gstore = "http://staging-api.globalforestwatch.org/geostore/4531cca6a8ddcf01bccf302b3dd7ae3f"
    r = requests.get(gstore)
    j = r.json()
    j = j.get('data').get('attributes').get('geojson')
    j['features'][0]['geometry']['type'] = "Polygon"
    j['features'][0]['geometry']['coordinates'] = j['features'][0]['geometry']['coordinates'][0][0]
    # Initilise an SQL2GEE query object with geojson
    q = SQL2GEE("SELECT ST_SUMMARYSTATS() FROM srtm90_v4", geojson=j)
    assert isinstance(q.geojson, ee.FeatureCollection), "FeatureCollection wasn't created from passed Geojson data"
    assert q.response == expected, "Response was not equal to expected values"
    return

def test_STSUMMARYSTATS_with_area_restriction_via_passing_geojson_multipolygon():
    """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
    This should then be used to subset the area considered for results."""
    # Get a test geojson object by accessing Vizzuality's geostore
    expected = {u'elevation': {'count': 118037,
                                'max': 489,
                                'mean': 326.5521573743826,
                                'min': 126,
                                'stdev': 75.69057079693977,
                                'sum': 38545237.0}}
    gstore = "http://staging-api.globalforestwatch.org/geostore/4531cca6a8ddcf01bccf302b3dd7ae3f"
    r = requests.get(gstore)
    j = r.json()
    j = j.get('data').get('attributes').get('geojson')
    # Initilise an SQL2GEE query object with geojson
    q = SQL2GEE("SELECT ST_SUMMARYSTATS() FROM srtm90_v4", geojson=j)
    assert isinstance(q.geojson, ee.FeatureCollection), "geojson data not converted to ee.FeatureCollection type"
    assert q.response == expected, "Area restricted response did not match expected result"
    return


def test_ST_SUMMARYSTATS_with_tricky_data():
    """A problem with image data that is a composite. We will try and get a response, if an EEException is raised,
    a default (near-global) feature collection will be passed to the area, which will cause reducers to correctly
    treat it like an image."""
    sql = "SELECT ST_SUMMARYSTATS() FROM GFSAD1000_V0"
    q = SQL2GEE(sql)
    assert isinstance(q.response, dict), "Dictionary should have been returned"
    return