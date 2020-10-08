import os
import sys
import ee
import requests

from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql

# Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    EE_ACCOUNT = os.environ['EE_ACCOUNT']
    EE_PRIVATE_KEY_FILE = 'privatekey.json'

    gee_credentials = ee.ServiceAccountCredentials(EE_ACCOUNT, EE_PRIVATE_KEY_FILE)
    ee.Initialize(gee_credentials)


def test_metadata():
    sql = "SELECT ST_HISTOGRAM(rast, elevation, 10, true) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())
    assert q.metadata['type'] == 'IMAGE'
    assert q.metadata['name'] == 'projects/earthengine-public/assets/CGIAR/SRTM90_V4'
    assert q.metadata['id'] == 'CGIAR/SRTM90_V4'
    assert q.metadata['title'] == 'SRTM Digital Elevation Data Version 4'
    assert 'properties' in q.metadata
    assert 'description' in q.metadata
    assert 'bands' in q.metadata
    return


def test_type():
    sql = "SELECT ST_HISTOGRAM(rast, elevation, 10, true) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())
    assert q.type == 'IMAGE'
    return


def test_retrieve_st_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_METADATA() command is given.
    Notes:
        CGIAR/SRTM90_V4 is a 90m Elevation image.
    """
    sql = "SELECT ST_METADATA(rast) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())

    result = q.response()[0]['st_metadata']

    assert result['type'] == 'IMAGE'
    assert result['name'] == 'projects/earthengine-public/assets/CGIAR/SRTM90_V4'
    assert result['id'] == 'CGIAR/SRTM90_V4'
    assert result['title'] == 'SRTM Digital Elevation Data Version 4'
    assert 'properties' in result
    assert 'description' in result
    assert 'bands' in result

    return


def test_retrieve_st_band_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_BANDMETADATA() command is given.
    Notes:
        CGIAR/SRTM90_V4 is a 90m Elevation image.
    """
    sql = "SELECT ST_BANDMETADATA(rast, elevation) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())

    result = q.response()[0]['st_bandmetadata']

    assert result['id'] == 'elevation'
    assert result['dataType'] == {'precision': 'INT', 'range': {'min': -32768, 'max': 32767}}
    assert result['grid'] == {'crsCode': 'EPSG:4326', 'dimensions': {'width': 432000, 'height': 144000},
                              'affineTransform': {'scaleX': 0.000833333333333, 'translateX': -180,
                                                  'scaleY': -0.000833333333333, 'translateY': 60}}
    assert result['pyramidingPolicy'] == 'MEAN'
    return


def test_ST_HISTOGRAM():
    """Test that a dictionary containing a list of expected length and values is returned"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM CGIAR/SRTM90_V4"
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
    assert isinstance(response, list), "Dictionary was not returned as a response"
    assert len(response) == 1, "Size of the dictionary was diffrent from expected response"
    assert list(response[0].keys()) == expected_keys, "Expected keys in response dictionary were not returned"
    for key in response[0][expected_keys[0]].keys():
        if response[0][expected_keys[0]][key] != None:
            assert len(response[0][expected_keys[0]][key]) == 36, "Expected 210 bins in histogram"
    return


def test_ST_HISTORGRAM_keywords_select_specific_band_and_bins():
    """Without any specific keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    expected_keys = ['st_histogram']
    sql = "SELECT ST_HISTOGRAM(raster, 'elevation', 10, true) FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()

    assert isinstance(response, list), "Dictionary was not returned as a response"
    assert len(response) == 1, "Size of the dictionary was diffrrent from expected response"

    assert list(response[0].keys()) == expected_keys, "Expected elevation in response dictionary"
    for key in response[0][expected_keys[0]].keys():
        if response[0][expected_keys[0]][key] != None:
            assert len(response[0][expected_keys[0]][key]) == 10, "Expected 10 bins in histogram"
    return


def test_ST_HISTORGRAM_keywords_reversed():
    """Without any specific keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    sql = "SELECT ST_HISTOGRAM(raster, 'elevation', 10, false) FROM 'CGIAR/SRTM90_V4'"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert response[0]['st_histogram']['elevation'][0][0] > response[0]['st_histogram']['elevation'][-1][
        0], "Bins should be in reverse order"
    return


def test_STSUMMARYSTATS():
    """Check an expected dictionary is returned via the ST_SUMMARYSTATS() keyword"""
    expected = [{u'st_summarystats': {u'elevation': {'count': 2747198,
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
    expected = [{u'st_summarystats': {
        u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 505.6705882352941, 'stdev': 4.272001872658765,
                       'mean': 1048.341463414634}}}]
    gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
    r = requests.get(gstore).json().get('data').get('attributes').get('geojson')

    # Initilise an SQL2GEE query object with geojson
    sql = "SELECT ST_SUMMARYSTATS() FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json(), geojson=r)
    response = q.response()
    assert response == expected, "Response was not equal to expected values"
    return


def test_STSUMMARYSTATS_with_area_restriction_via_passing_geojson_multipolygon():
    """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
    This should then be used to subset the area considered for results."""
    # Get a test geojson object by accessing Vizzuality's geostore
    expected = [{u'st_summarystats': {
        u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 505.6705882352941, 'stdev': 4.272001872658765,
                       'mean': 1048.341463414634}}}]
    gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
    r = requests.get(gstore).json().get('data').get('attributes').get('geojson')
    # Initialise an SQL2GEE query object with geojson
    sql = "SELECT ST_SUMMARYSTATS() FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json(), geojson=r)
    response = q.response()
    assert response == expected, "Area restricted response did not match expected result"
    return


def test_ST_SUMMARYSTATS_with_tricky_data():
    """A problem with image data that is a composite. We will try and get a response, if an EEException is raised,
    a default (near-global) feature collection will be passed to the area, which will cause reducers to correctly
    treat it like an image."""
    sql = 'SELECT ST_SUMMARYSTATS() FROM "USGS/GFSAD1000_V1"'
    q = SQL2GEE(JsonSql(sql).to_json())
    assert isinstance(q.response(), list), "Dictionary should have been returned"
    return


def test_ST_HISTOGRAM_bins_correct():
    """Hansen Forest change dataset has a band called lossyear, which has integer values of 0->14.
    Make a test to create a bin for each integer."""
    sql = 'SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM "UMD/hansen/global_forest_change_2019_v1_7"'
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert len(response[0]['st_histogram']['lossyear']) == 15, "15 bins expected"
    assert response[0]['st_histogram']['lossyear'][14][0] == 18.733333333333334
    return


def test_ST_GeomFromGeoJSON():
    """Test that SQL queries can set a geojson object that gets correctly used."""
    sql = """SELECT ST_SUMMARYSTATS() as x FROM 'CGIAR/SRTM90_V4'
                 WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Polygon\",
                 \"coordinates\":[[[-43.39599609375,-4.740675384778361],
                 [-43.39599609375,-4.959615024698014],
                 [-43.17626953125,-4.806364708499984],
                 [-43.39599609375,-4.740675384778361]]]}'),4326), the_geom)"""

    correct = {'x': {'elevation': {'count': 35205, 'sum': 3465299.4509803923, 'mean': 100.04437654442181,
                                   'stdev': 21.970242559380736, 'min': 52, 'max': 172}}}

    jsonQuery = JsonSql(sql).to_json()
    q = SQL2GEE(jsonQuery)
    response = q.response()[0]

    assert response['x']['elevation']['min'] == correct['x']['elevation']['min'], "Incorrect response returned"
    return


def test_auto_bug():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())
    try:
        _ = q.response()
    except:
        # If the response failed to retun fail this test...
        assert q.response() == None
    return


def test_band_byname():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 'elevation', auto, true) FROM CGIAR/SRTM90_V4"
    q = SQL2GEE(JsonSql(sql).to_json())
    try:
        _ = q.response()
    except:
        # If the response failed to return fail this test...
        assert q.response == None
    return


def test_valuecount_categorical():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', false) as t FROM 'JRC/GSW1_2/GlobalSurfaceWater'"
    correct = [{'t': {
        'seasonality': {'1': 269354, '10': 13929, '11': 2506, '12': 19746788, '2': 79053, '3': 18373, '4': 11953,
                        '5': 11982, '6': 3361, '7': 60005, '8': 17058, '9': 20501}}}]
    q = SQL2GEE(JsonSql(sql).to_json())
    assert q.response() == correct, "Incorrect response returned"
    return


def test_valuecount_categorical_true():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', true) FROM 'JRC/GSW1_2/GlobalSurfaceWater'"
    correct = [{'st_valuecount': {
        'seasonality': {'1': 257090.0, '10': 53411.0, '11': 3326.0, '12': 18471661.0, '2': 86180.0, '3': 17032.0,
                        '4': 40943.0, '5': 27166.0, '6': 4363.0, '7': 150599.0, '8': 30365.0, '9': 68880.0,
                        'null': 673491564.0}}}]
    q = SQL2GEE(JsonSql(sql).to_json())
    assert q.response() == correct, "Incorrect response returned"
    return


def test_valuecount_categorical_true():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', true) FROM 'JRC/GSW1_0/GlobalSurfaceWater'"
    correct = [{'st_valuecount': {
        'seasonality': {'1': 257090.0, '10': 53411.0, '11': 3326.0, '12': 18471661.0, '2': 86180.0, '3': 17032.0,
                        '4': 40943.0, '5': 27166.0, '6': 4363.0, '7': 150599.0, '8': 30365.0, '9': 68880.0,
                        'null': 673491564.0}}}]
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()

    assert response == correct, "Incorrect response returned"
    return
