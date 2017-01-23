from __future__ import print_function, division
import pytest
import sys
from sql2gee import SQL2GEE
import ee
from ee import Feature, Image, Initialize

# quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    # Else, assume you have an EE_private_key environment variable with authorisation...
    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
    ee.Initialize(credentials, 'https://earthengine.googleapis.com')


def test_basic_table_query():
    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100'
    q = SQL2GEE(sql)
    assert q.response == 1919, "Basic query incorrect"
    return


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
    error = q.metadata != ee_meta
    assert not error, 'test metadata not equal to expected metadata'
    return


def test_histogram():
    # pytest.skip("Need to initilise on Travis")
    sql = "SELECT ST_HISTOGRAM() FROM srtm90_v4"
    q = SQL2GEE(sql)
    num_bins = len(q.histogram['elevation'])
    assert num_bins == 753, "Should be 753 bins by default (set by Freedman-Diaconis method)"
    assert q.response['elevation'][0] == [-415.0, 14.0], 'First bin incorrect'
    assert q.response['elevation'][-1] == [7148.941567065073, 0.0], 'Last bin incorrect'
    return


def test_limit_on_tables():
    sql = 'select width from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT '
    err = 'Response was not equal to size of LIMIT'
    limit = 1
    r = SQL2GEE(sql + str(limit))
    assert len(r.response['features']) == limit, err
    limit = 2
    r = SQL2GEE(sql + str(limit))
    assert len(r.response['features']) == limit, err
    limit = 5
    r = SQL2GEE(sql + str(limit))
    assert len(r.response['features']) == limit, err
