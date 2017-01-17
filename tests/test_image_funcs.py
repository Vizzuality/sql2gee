from __future__ import print_function
import pytest
from sql2gee import SQL2GEE
from ee import Feature, Image, Initialize
import pprint


@pytest.mark.skip(reason="Needs to be initilised to pass.")
def test_retrieve_raw_ee_raster_metadata():
    """Test that basic raster metadata (in dictionary format) is returned when
    the postgis ST_METADATA() command is given.
    Notes:
        srtm90_v4 is a 90m Elevation image.
        The user will be expected to know if they are requesting an image or feature.
    """
    Initialize()
    q = SQL2GEE("SELECT ST_METADATA(*) FROM srtm90_v4")
    # test_meta = Image('srtm90_v4').getInfo()  # Earth Engine metadata
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
    # pprint.pprint(ee_meta)  # To print in a human-friendly way
    test_meta = q._ee_image_metadata
    error = test_meta != ee_meta
    print("SQL2GEE retrieved: ", test_meta)
    assert not error, 'test metadata not equal to expected metadata'
    return