import numpy as np
import requests
import sys
import pytest
from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql
import ee

# Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    # Else, assume you have an EE_private_key environment variable with authorisation, as on Travis-CI
    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
    ee.Initialize(credentials, 'https://earthengine.googleapis.com')

def test_metadata():
   sql = "SELECT ST_HISTOGRAM(rast, elevation, 10, true) FROM srtm90_v4"
   q = SQL2GEE(JsonSql(sql).to_json())
   assert q.metadata == {'type': 'Image', 'bands': [{'id': 'elevation', 'data_type': {'type': 'PixelType', 'precision': 'int', 'min': -32768, 'max': 32767}, 'dimensions': [432000, 144000], 'crs': 'EPSG:4326', 'crs_transform': [0.000833333333333, 0.0, -180.0, 0.0, -0.000833333333333, 60.0]}], 'version': 1494271934303000, 'id': 'srtm90_v4', 'properties': {'system:time_start': 950227200000, 'system:time_end': 951177600000, 'system:asset_size': 18827626666}}
   return

def test_type():
   sql = "SELECT ST_HISTOGRAM(rast, elevation, 10, true) FROM srtm90_v4"
   q = SQL2GEE(JsonSql(sql).to_json())
   assert q.type == 'Image'
   return

def test_retrieve_st_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_METADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
    """
    sql = "SELECT ST_METADATA(rast) FROM srtm90_v4"
    q = SQL2GEE(JsonSql(sql).to_json())
    ee_meta = {'type': 'Image', 'bands': [{'id': 'elevation', 'data_type': {'type': 'PixelType', 'precision': 'int', 'min': -32768, 'max': 32767}, 'dimensions': [432000, 144000], 'crs': 'EPSG:4326', 'crs_transform': [0.000833333333333, 0.0, -180.0, 0.0, -0.000833333333333, 60.0]}], 'version': 1494271934303000, 'id': 'srtm90_v4', 'properties': {'system:time_start': 950227200000, 'system:time_end': 951177600000, 'system:asset_size': 18827626666}}
    print(q.response())
    assert q.response()[0]['st_metadata'] == ee_meta, 'Metadata response was not equal to expected metadata'
    return

def test_retrieve_st_bandmetadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_BANDMETADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
    """
    sql = "SELECT ST_BANDMETADATA(rast, elevation) FROM srtm90_v4"
    q = SQL2GEE(JsonSql(sql).to_json())
    ee_meta = {u'crs': u'EPSG:4326',
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
                 u'id': u'elevation'}
    print(q.response())
    assert q.response()[0]['st_bandmetadata'] == ee_meta, 'Band Metadata response was not equal to expected band metadata'
    return

def test_ST_HISTOGRAM():
    """Test that a dictionary containing a list of expected length and values is returned"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM srtm90_v4"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()[0]['st_histogram']
    assert response['elevation'][0] == [-32.0, 5.149019607843137], 'First bin incorrect'
    assert response['elevation'][-1] == [1088.0, 1.0], 'Last bin incorrect'
    return


def test_ST_HISTORGRAM_multiband_image():
    """ST_HISTOGRAM should give back a dic with the first band, and best-guess binning if auto argument is specified"""
    expected_keys = ['st_histogram']
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    print(response)
    assert isinstance(response, list), "Dictionary was not returned as a response"
    assert len(response) == 1, "Size of the dictionary was diffrent from expected response"
    assert list(response[0].keys()) == expected_keys, "Expected keys in response dictionary were not returned"
    for key in response[0][expected_keys[0]].keys():
        if response[0][expected_keys[0]][key] != None:
            assert len(response[0][expected_keys[0]][key]) == 36, "Expected 210 bins in histogram"
    return

def test_ST_HISTORGRAM_keywords_select_specific_band_and_bins():
    """Without any speicifc keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    expected_keys = ['st_histogram']
    sql = "SELECT ST_HISTOGRAM(raster, 'elevation', 10, true) FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    
    assert isinstance(response, list), "Dictionary was not returned as a response"
    assert len(response) == 1, "Size of the dictionary was diffrent from expected response"
    
    assert list(response[0].keys()) == expected_keys, "Expected elevation in response dictionary"
    for key in response[0][expected_keys[0]].keys():
        if response[0][expected_keys[0]][key] != None:
            assert len(response[0][expected_keys[0]][key]) == 10, "Expected 10 bins in histogram"
    return

def test_ST_HISTORGRAM_keywords_reversed():
    """Without any speicifc keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    sql = "SELECT ST_HISTOGRAM(raster, 'elevation', 10, false) FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert response[0]['st_histogram']['elevation'][0][0] >  response[0]['st_histogram']['elevation'][-1][0], "Bins should be in reverse order"
    return

def test_STSUMMARYSTATS():
    """Check an expected dictionary is returned via the ST_SUMMARYSTATS() keyword"""
    expected = [{u'st_summarystats':{u'elevation': {'count': 2747198,
                                'max': 7159,
                                'mean': 689.8474833769903,
                                'min': -415,
                                'stdev': 865.9582784994756,
                                'sum': 1859471136.0274282}}}]
    sql = "SELECT ST_SUMMARYSTATS() FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    q.response() == expected, "Summary stats did not match expected result"
    return

def test_STSUMMARYSTATS_with_area_restriction_from_geojson_polygon():
   """First, I need to construct a simple polygon out of multipolygon data, and pass that to SQL2GEE"""
   expected = [{u'st_summarystats':{u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 460.5490196078431, 'stdev': 4.272001872658765, 'mean': 1048.5714285714284}}}]
   gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
   r = requests.get(gstore).json().get('data').get('attributes').get('geojson')
   
   # Initilise an SQL2GEE query object with geojson
   sql = "SELECT ST_SUMMARYSTATS() FROM srtm90_v4"
   q = SQL2GEE(JsonSql(sql).to_json(), geojson=r)
   response = q.response()
   assert response == expected, "Response was not equal to expected values"
   return

def test_STSUMMARYSTATS_with_area_restriction_via_passing_geojson_multipolygon():
   """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
   This should then be used to subset the area considered for results."""
   # Get a test geojson object by accessing Vizzuality's geostore
   expected = [{u'st_summarystats':{u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 460.5490196078431, 'stdev': 4.272001872658765, 'mean': 1048.5714285714284}}}]
   gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
   r = requests.get(gstore).json().get('data').get('attributes').get('geojson')
   print(r)
   # Initilise an SQL2GEE query object with geojson
   sql = "SELECT ST_SUMMARYSTATS() FROM srtm90_v4"
   q = SQL2GEE(JsonSql(sql).to_json(), geojson=r)
   response=q.response()
   assert response == expected, "Area restricted response did not match expected result"
   return

def test_ST_SUMMARYSTATS_with_tricky_data():
    """A problem with image data that is a composite. We will try and get a response, if an EEException is raised,
    a default (near-global) feature collection will be passed to the area, which will cause reducers to correctly
    treat it like an image."""
    sql = 'SELECT ST_SUMMARYSTATS() FROM "USGS/GFSAD1000_V0"'
    q = SQL2GEE(JsonSql(sql).to_json())
    assert isinstance(q.response(), list), "Dictionary should have been returned"
    return

def test_ST_HISTOGRAM_bins_correct():
    """Hansen Forest change dataset has a band called lossyear, which has integer values of 0->14.
    Make a test to create a bin for each integer."""
    sql = 'SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM "UMD/hansen/global_forest_change_2015"'
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert len(response[0]['st_histogram']['lossyear']) == 15, "15 bins expected"
    assert response[0]['st_histogram']['lossyear'][14][0] == 14, "Expected last bin to be 14 exactly"
    return

def test_ST_GeomFromGeoJSON():
  """Test that SQL queries can set a geojson object that gets correctly used."""
  sql = """SELECT ST_SUMMARYSTATS() as x FROM 'srtm90_v4'
                 WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Polygon\",
                 \"coordinates\":[[[-43.39599609375,-4.740675384778361],
                 [-43.39599609375,-4.959615024698014],
                 [-43.17626953125,-4.806364708499984],
                 [-43.39599609375,-4.740675384778361]]]}'),4326), the_geom)"""
  
  correct = [{'x': {'elevation': {'count': 35178, 'sum': 3464822.050980393, 'mean': 100.03593960771832, 'stdev': 21.969258118520724, 'min': 52, 'max': 172}}}]

  q = SQL2GEE(JsonSql(sql).to_json())
  
  assert q.response()[0]['x']['elevation']['count'] == correct[0]['x']['elevation']['count'], "Incorrect response returned"
  return

def test_auto_bug():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM srtm90_v4"
    q = SQL2GEE(JsonSql(sql).to_json())
    try:
        _ = q.response()
    except:
        # If the response failed to retun fail this test...
        assert q.response() == None
    return

def test_band_byname():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 'elevation', auto, true) FROM srtm90_v4"
    q = SQL2GEE(JsonSql(sql).to_json())
    try:
        _=q.response()
    except:
        # If the response failed to retun fail this test...
        assert q.response == None
    return

def test_valuecount_categorical():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', false) as t FROM 'JRC/GSW1_0/GlobalSurfaceWater'"
    correct = [{'t': {'seasonality': {'1': 257090.0, '10': 53411.0, '11': 3326.0, '12': 18471661.0, '2': 86180.0, '3': 17032.0, '4': 40943.0, '5': 27166.0, '6': 4363.0, '7': 150599.0, '8': 30365.0, '9': 68880.0}}}]
    q = SQL2GEE(JsonSql(sql).to_json())
    assert q.response() == correct, "Incorrect response returned"
    return
def test_valuecount_categorical_true():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', true) FROM 'JRC/GSW1_0/GlobalSurfaceWater'"
    correct = [{'st_valuecount': {'seasonality': {'1': 257090.0, '10': 53411.0, '11': 3326.0, '12': 18471661.0, '2': 86180.0, '3': 17032.0, '4': 40943.0, '5': 27166.0, '6': 4363.0, '7': 150599.0, '8': 30365.0, '9': 68880.0, 'null': 673491564.0}}}]
    q = SQL2GEE(JsonSql(sql).to_json())
    print(q.response())
    assert q.response() == correct, "Incorrect response returned"
    return
