import ee
from image import Image
from image_collection import ImageCollection
from feature_collection import FeatureCollection

ee.Initialize()

class GeeFactory(object):
  """docstring for GeeFactory"""
  def __init__(self, json, geojson=None, flags=None):
    super(GeeFactory, self).__init__()
    self.json = json
    self._asset_id = json['data']['attributes']['jsonSql']['from'].strip("'")
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
      return Image().response()
    elif self.type == 'ImageCollection':
      return ImageCollection(self.json, self._asset_id).response()
    elif self.type == 'FeatureCollection':
      return FeatureCollection(self.json, self._asset_id, self.geojson).response()
