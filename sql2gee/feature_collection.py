import ee
import json
from collection import Collection

ee.Initialize()

class FeatureCollection(Collection):
  """docstring for FeatureCollection"""
  def __init__(self, json, asset_id, geojson=None):
    self.json = json
    self.asset_id = asset_id
    self._parsed = json['data']['attributes']['jsonSql']
    self.geojson = self._geojson_to_featurecollection(geojson)
    Collection.__init__(self, self._parsed, self.asset_id, 'FeatureCollection', self.geojson)

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
    (containing geojson data) convert it into a useable E.E. object."""
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

  def response(self):
    if 'where' in self._parsed:
      assembled = self._where()
    else:
      assembled = self._asset

    if 'limit' in self._parsed:
      assembled = assembled.limit(self._limit())

    if 'orderBy' in self._parsed:
      assembled = assembled.sort(self._sort())

    return assembled.getInfo()
    # FeatureCollection.<filters>.<functions>.<sorts>.limit(n).getInfo()
    