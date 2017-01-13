import unittest
from sql2gee import SQL2GEE
from ee import Filter, Image, Initialize
import pprint

Initialize()

def test_simple_raster_metadata():
    """Base case of calling raster metadata with postgis ST_METADATA() command
    Notes:
        srtm90_v4 is a 90m Elevation image.
        The user will be expected to know if they are requesting an image or feature.
    """
    q = SQL2GEE("SELECT ST_METADATA(*) FROM srtm90_v4")
    image = Image('srtm90_v4')
    ee_meta = image.getInfo()  # Earth Engine metadata
    pprint.pprint(ee_meta) # To print in a human-friendly way
    test_meta = q.image_metadata
    unittest.TestCase.assertEqual(test_meta, ee_meta)
    return


