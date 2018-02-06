import ee
import json
from image import Image
#from json_sql import JsonSql
from image_collection import ImageCollection
from feature_collection import FeatureCollection

ee.Initialize()

class GeeFactory(object):

  """docstring for GeeFactory"""
  def __init__(self, sqlscheme, geojson=None, flags=None):
    self.json = sqlscheme
    self._parsed = self.json['data']['attributes']['jsonSql']
    self.sql = self.json['data']['attributes']['query']
    self._asset_id = self.json['data']['attributes']['jsonSql']['from'].strip("'")
    self.type = self.metadata()['type']
    self.geojson = geojson 
    self.flags = flags  # <-- Will be used in a later version of the code

  def _geo_extraction(self, json_input):
    lookup_key = 'type'
    lookup_value = 'function'
    Sqlfunction = 'ST_GeomFromGeoJSON'

    if isinstance(json_input, dict):
      for k, v in json_input.items():
        if k == lookup_key and v == lookup_value and json_input['value'] == Sqlfunction:
          yield json_input['arguments'][0]['value'].strip("'")
        else:
          for child_val in self._geo_extraction(v):
            yield child_val
    elif isinstance(json_input, list):
      for item in json_input:
        for item_val in self._geo_extraction(item):
          yield item_val

  def _geojson_to_featurecollection(self, geojson):
    """If Geojson kwarg is recieved or ST_GEOMFROMGEOJSON sql argument is used,
    (convert it into a useable E.E. object.ontaining geojson data) c"""
    geometries = [json.loads(x) for x in self._geo_extraction(self._parsed)]

    if geometries:
      geojson = {
        u'features': geometries,
        u'type': u'FeatureCollection'
      }

    if isinstance(geojson, dict):
      assert geojson.get('features') != None, "Expected key not found in item passed to geojoson"
      return ee.FeatureCollection(geojson.get('features'))
    else:
      return None

  def metadata(self):
    """Property that holds the Metadata dictionary returned from Earth Engine."""
    if 'ft:' in self._asset_id:
      meta = ee.FeatureCollection(self._asset_id).limit(0).getInfo()
      assert meta != None, 'please enter a valid fusion table'

      info = {
        'type': meta['type'],
        'columns':meta['columns'],
        'id':self._asset_id,
        'version':'',
        'properties':meta['properties']
      }

      return info
    else:
      info = ee.data.getInfo(self._asset_id)
      assert info != None, "data type not expected"

      if ('bands' in info) and (not info['bands']):
        meta = ee.ImageCollection(self._asset_id).limit(1).getInfo()['features'][0] ### this is a bit ... 
        info['bands'] = meta['bands']
        info['columns'] = { k: type(v).__name__  for k,v in meta['properties'].items() }
              
    return info
    
  def response(self):
    _default_geojson = {
    u'crs':'EPSG:4326',
    u'features': [
        {
          u'geometry': dict(coordinates=[[[
              [1.40625,85.1114157806266],
              [0,-84.99010018023479],
              [-180,-85.05112877980659],
              [-180,85.1114157806266]]],
              [[[179.296875,85.05112877980659],
              [1.40625,85.05112877980659],
              [0.703125,-84.99010018023479],
              [179.296875,-84.86578186731522]]]],
            evenOdd= True,
            type= u'MultiPolygon'),
          u'type': u'Feature'
        }
      ],
      u'type': u'FeatureCollection'
    }
    imGeom = self.geojson if self.geojson else _default_geojson # To avoid the image composite bug we add a global region to group the image together.
    collGeom = self._geojson_to_featurecollection(self.geojson)
    fnResponse={
    'Image': Image(self.sql, self.json, imGeom).response,
    'ImageCollection': ImageCollection(self.json, self._asset_id, collGeom).response,
    'FeatureCollection': FeatureCollection(self.json, self._asset_id, collGeom).response
    }
    
    try:
      return fnResponse[self.type]()
    except ee.EEException:
        # raise Error
        print('GEEFactory Exception: ')
        raise
        
    
