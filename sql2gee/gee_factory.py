import ee
from image import Image
from json_sql import JsonSql
from image_collection import ImageCollection
from feature_collection import FeatureCollection

ee.Initialize()

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

class GeeFactory(object):
  """docstring for GeeFactory"""
  def __init__(self, sql, geojson=None, flags=None):
    super(GeeFactory, self).__init__()
    self.sql = sql
    self.json = JsonSql(sql).to_json()
    self._asset_id = self.json['data']['attributes']['jsonSql']['from'].strip("'")
    self.type = self.metadata()['type']
    self.geojson = geojson
    self.flags = flags  # <-- Will be used in a later version of the code

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
    if self.type == 'Image':
      try:
        return Image(self.sql, self.json, self.geojson).response()
      except ee.EEException:
        # If we hit the image composite bug then add a global region to group the image together and try again
        return GeeFactory(self.sql, _default_geojson).response()
    elif self.type == 'ImageCollection':
      return ImageCollection(self.json, self._asset_id).response()
    elif self.type == 'FeatureCollection':
      return FeatureCollection(self.json, self._asset_id, self.geojson).response()
