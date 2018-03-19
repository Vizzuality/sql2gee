import numpy as np
import requests
import sys
import pytest
from sql2gee.sql2gee import SQL2GEE
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
   sql = "SELECT ST_HISTOGRAM(rast, elevation, 10, true) FROM srtm90_v4"
   q = SQL2GEE(sql)
   assert q._band_names == ['elevation']
   return

def test_retrieve_st_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_METADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
    """
    q = SQL2GEE("SELECT ST_METADATA(rast) FROM srtm90_v4")
    ee_meta = {u'system:asset_size': 18827626666,
               u'system:time_end': 951177600000,
               u'system:time_start': 950227200000,
               u'bands':[{
                          "id": "elevation",
                          "data_type": {
                            "type": "PixelType",
                            "precision": "int",
                            "min": -32768,
                            "max": 32767
                          },
                          "dimensions": [
                            432000,
                            144000
                          ],
                          "crs": "EPSG:4326",
                          "crs_transform": [
                            0.000833333333333,
                            0,
                            -180,
                            0,
                            -0.000833333333333,
                            60
                          ]
                        }]
            }
    assert q.response == ee_meta, 'Metadata response was not equal to expected metadata'
    return

def test_retrieve_st_bandmetadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_BANDMETADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
    """
    q = SQL2GEE("SELECT ST_BANDMETADATA(rast, elevation) FROM srtm90_v4")
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
    assert q.response == ee_meta, 'Band Metadata response was not equal to expected band metadata'
    return

def test_ST_HISTOGRAM():
    """Test that a dictionary containing a list of expected length and values is returned"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM srtm90_v4"
    q = SQL2GEE(sql)
    num_bins = len(q.response['elevation'])
    assert num_bins == 753, "Should be 753 bins by default (set by Freedman-Diaconis method)"
    assert q.response['elevation'][0] == [-415.0, 14.0], 'First bin incorrect'
    assert q.response['elevation'][-1] == [7149.940239043825, 1.0], 'Last bin incorrect'
    return


def test_ST_HISTORGRAM_multiband_image():
    """ST_HISTOGRAM should give back a dic with the first band, and best-guess binning if auto argument is specified"""
    expected_keys = [u'elevation']
    q = SQL2GEE("SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM 'CGIAR/SRTM90_V4'")
    assert isinstance(q.response, dict), "Dictionary was not returned as a response"
    assert len(q.response) == 1, "Size of the dictionary was diffrent from expected response"
    assert q.response.keys() == expected_keys, "Expected keys in response dictionary were not returned"
    for key in q.response.keys():
        if q.response[key] != None:
            assert len(q.response[key]) == 753, "Expected 210 bins in histogram"
    return

def test_ST_HISTORGRAM_keywords_select_specific_band_and_bins():
    """Without any speicifc keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    expected_keys = [u'elevation']
    q = SQL2GEE("SELECT ST_HISTOGRAM(raster, 'elevation', 10, true) FROM 'CGIAR/SRTM90_V4'")
    assert isinstance(q.response, dict), "Dictionary was not returned as a response"
    assert len(q.response) == 1, "Size of the dictionary was diffrent from expected response"
    assert q.response.keys() == expected_keys, "Expected elevation in response dictionary"
    for key in q.response.keys():
        if q.response[key] != None:
            assert len(q.response[key]) == 10, "Expected 10 bins in histogram"
    return

def test_ST_HISTORGRAM_keywords_reversed():
    """Without any speicifc keywords set, ST_HISTOGRAM gives back a dic with the first band, and best-guess binning"""
    q = SQL2GEE("SELECT ST_HISTOGRAM(raster, 1, 10, false) FROM srtm90_v4")
    assert q.response['elevation'][0][0] > q.response['elevation'][-1][0], "Bins should be in reverse order"
    return

def test_ST_HISTOGRAM_with_area_restriction():
    """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
    This should then be used to subset the area considered for results."""
    # Get a test geojson object by accessing Vizzuality's geostore
    gstore = "https://api.resourcewatch.org/v1/geostore/4f91a9a8af95148a7c962ffad6683e04"
    r = requests.get(gstore)
    j = r.json()
    j = j.get('data').get('attributes').get('geojson')
    # Initilise an SQL2GEE query object with geojson
    q = SQL2GEE("SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM srtm90_v4", geojson=j)
    assert isinstance(q.geojson, ee.FeatureCollection), "Geojson data not converted to ee.FeatureCollection type"
    assert len(q.response['elevation']) == 538, "Returned area-restricted histogram not equal to len of expected result"
    flist = [freq for x, freq in q.response['elevation']]
    assert np.mean(flist) == 4302.8145929003576, "Values returned from histogram dont match expected"
    assert q.response['elevation'][0] == [175.0, 1.0], "Returned bins don't match expected values"
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
   expected = {u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 460.5490196078431, 'stdev': 4.272001872658765, 'mean': 1048.5714285714284}}
   gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
   r = requests.get(gstore)
   j = r.json()
   j = j.get('data').get('attributes').get('geojson')
   # Initilise an SQL2GEE query object with geojson
   q = SQL2GEE("SELECT ST_SUMMARYSTATS() FROM srtm90_v4", geojson=j)
   print(q.response)
   assert isinstance(q.geojson, ee.FeatureCollection), "FeatureCollection wasn't created from passed Geojson data"
   assert q.response == expected, "Response was not equal to expected values"
   return

def test_STSUMMARYSTATS_with_area_restriction_via_passing_geojson_multipolygon():
   """If a geojson argument is passed to SQL2GEE it should be converted into an Earth Engine Feature Collection.
   This should then be used to subset the area considered for results."""
   # Get a test geojson object by accessing Vizzuality's geostore
   expected = {u'elevation': {'count': 4, 'min': 1041, 'max': 1051, 'sum': 460.5490196078431, 'stdev': 4.272001872658765, 'mean': 1048.5714285714284}}
   gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
   r = requests.get(gstore)
   j = r.json()
   j = j.get('data').get('attributes').get('geojson')
   # Initilise an SQL2GEE query object with geojson
   q = SQL2GEE("SELECT ST_SUMMARYSTATS() FROM srtm90_v4", geojson=j)
   print(q.response)
   assert isinstance(q.geojson, ee.FeatureCollection), "geojson data not converted to ee.FeatureCollection type"
   assert q.response == expected, "Area restricted response did not match expected result"
   return

def test_ST_SUMMARYSTATS_with_tricky_data():
    """A problem with image data that is a composite. We will try and get a response, if an EEException is raised,
    a default (near-global) feature collection will be passed to the area, which will cause reducers to correctly
    treat it like an image."""
    sql = 'SELECT ST_SUMMARYSTATS() FROM "USGS/GFSAD1000_V0"'
    q = SQL2GEE(sql)
    assert isinstance(q.response, dict), "Dictionary should have been returned"
    return

def test_ST_HISTOGRAM_bins_correct():
    """Hansen Forest change dataset has a band called lossyear, which has integer values of 0->14.
    Make a test to create a bin for each integer."""
    sql = 'SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM "UMD/hansen/global_forest_change_2015"'
    q = SQL2GEE(sql)
    assert len(q.response['lossyear']) == 15, "15 bins expected"
    assert q.response['lossyear'][14][0] == 14, "Expected last bin to be 14 exactly"
    return

def test_ST_GeomFromGeoJSON():
   """Test that SQL queries can set a geojson object that gets correctly used."""
   sql = ''.join(["SELECT ST_SUMMARYSTATS() FROM 'srtm90_v4'",
                  "WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON(",
                  '{"type":"Polygon",',
                  '"coordinates":[[[-43.39599609375,-4.740675384778361],'
                  '[-43.39599609375,-4.959615024698014],'
                  '[-43.17626953125,-4.806364708499984],'
                  '[-43.39599609375,-4.740675384778361]]]}'
                  "),4326), the_geom)"])
   correct = {u'elevation': {'count': 35178, 'min': 52, 'max': 172, 'sum': 3464823.2431372553, 'stdev': 21.969258118520724, 'mean': 100.03588341657131}}
   q = SQL2GEE(sql)
   assert q.geojson, "Geojson was None"
   assert q.response == correct, "Incorrect response returned"
   return

def test_auto_bug():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 1, auto, true) FROM srtm90_v4"
    q = SQL2GEE(sql)
    try:
        _ = q.response
    except:
        # If the response failed to retun fail this test...
        assert q.response == None

def test_band_byname():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_HISTOGRAM(rast, 'elevation', auto, true) FROM srtm90_v4"
    q = SQL2GEE(sql)
    try:
        _=q.response
    except:
        # If the response failed to retun fail this test...
        assert q.response == None

def test_valuecount_categorical():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', false) FROM 'JRC/GSW1_0/GlobalSurfaceWater'"
    correct = {u'seasonality': {u'-49': 108.0, u'-42': 98.0, u'-43': 113.0, u'-40': 105.0, u'-47': 147.0, u'-44': 2.0, u'-45': 189.0, u'4': 4250136.0, u'8': 4444857.0, u'-72': 141.0, u'12': 251127101.0, u'-39': 1.0, u'-38': 197.0, u'-36': 90.0, u'-35': 93.0, u'-34': 13.0, u'-33': 128.0, u'-31': 208.0, u'-5': 1.0, u'-4': 145.0, u'-6': 135.0, u'-1': 137.0, u'-3': 106.0, u'-2': 95.0, u'-9': 15.0, u'-8': 103.0, u'-102': 1216766.0, u'-28': 1.0, u'-29': 140.0, u'-24': 187.0, u'-25': 1.0, u'-26': 110.0, u'-27': 128.0, u'-20': 112.0, u'-21': 1.0, u'-22': 88.0, u'3': 6144515.0, u'7': 4257271.0, u'-99': 270.0, u'-100': 260.0, u'-91': 46.0, u'-90': 145.0, u'-93': 172.0, u'-92': 113.0, u'-95': 148.0, u'-97': 228.0, u'-11': 106.0, u'-10': 169.0, u'-13': 129.0, u'-15': 159.0, u'-17': 171.0, u'-19': 83.0, u'-18': 53.0, u'-88': 177.0, u'-86': 174.0, u'-84': 120.0, u'-83': 78.0, u'-81': 197.0, u'2': 10609474.0, u'6': 3372212.0, u'11': 12119897.0, u'10': 7748423.0, u'-70': 118.0, u'-77': 106.0, u'-76': 95.0, u'-75': 48.0, u'-74': 186.0, u'-79': 114.0, u'-60': 114.0, u'-61': 143.0, u'-63': 129.0, u'-65': 112.0, u'-66': 17.0, u'-67': 164.0, u'-68': 90.0, u'-69': 1.0, u'1': 15517040.0, u'5': 3692893.0, u'9': 5583862.0, u'-54': 97.0, u'-57': 1.0, u'-56': 116.0, u'-51': 96.0, u'-53': 12.0, u'-52': 199.0, u'-59': 69.0, u'-58': 133.0}}
    q = SQL2GEE(sql)
    print(q.response)
    assert q.response == correct, "Incorrect response returned"
    try:
        _=q.response
    except:
        # If the response failed to retun fail this test...
        assert q.response == None
def test_valuecount_categorical_true():
    """Test a bug that was noticed regarding the use of auto as an argument"""
    sql = "SELECT ST_valuecount(rast, 'seasonality', true) FROM 'JRC/GSW1_0/GlobalSurfaceWater'"
    correct = {u'seasonality': {u'-49': 108.0, u'-42': 98.0, u'-43': 113.0, u'-40': 105.0, u'-47': 147.0, u'-44': 2.0, u'-45': 189.0, u'4': 4250136.0, u'8': 4444857.0, u'-72': 141.0, u'12': 251127101.0, u'-39': 1.0, u'-38': 197.0, u'-36': 90.0, u'-35': 93.0, u'-34': 13.0, u'-33': 128.0, u'-31': 208.0, u'-5': 1.0, u'-4': 145.0, u'-6': 135.0, u'-1': 137.0, u'-3': 106.0, u'-2': 95.0, u'-9': 15.0, u'-8': 103.0, u'-102': 1216766.0, u'-28': 1.0, u'-29': 140.0, u'-24': 187.0, u'-25': 1.0, u'-26': 110.0, u'-27': 128.0, u'-20': 112.0, u'-21': 1.0, u'-22': 88.0, u'3': 6144515.0, u'7': 4257271.0, u'-99': 270.0, u'-100': 260.0, u'-91': 46.0, u'-90': 145.0, u'-93': 172.0, u'-92': 113.0, u'-95': 148.0, u'-97': 228.0, u'-11': 106.0, u'-10': 169.0, u'-13': 129.0, u'-15': 159.0, u'-17': 171.0, u'-19': 83.0, u'-18': 53.0, u'-88': 177.0, u'-86': 174.0, u'-84': 120.0, u'-83': 78.0, u'-81': 197.0, u'2': 10609474.0, u'6': 3372212.0, u'11': 12119897.0, u'10': 7748423.0, u'-70': 118.0, u'-77': 106.0, u'-76': 95.0, u'-75': 48.0, u'-74': 186.0, u'-79': 114.0, u'null': 6506793674.0, u'-60': 114.0, u'-61': 143.0, u'-63': 129.0, u'-65': 112.0, u'-66': 17.0, u'-67': 164.0, u'-68': 90.0, u'-69': 1.0, u'1': 15517040.0, u'5': 3692893.0, u'9': 5583862.0, u'-54': 97.0, u'-57': 1.0, u'-56': 116.0, u'-51': 96.0, u'-53': 12.0, u'-52': 199.0, u'-59': 69.0, u'-58': 133.0}}
    q = SQL2GEE(sql)
    print(q.response)
    assert q.response == correct, "Incorrect response returned"
    try:
        _=q.response
    except:
        # If the response failed to retun fail this test...
        assert q.response == None
