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

  def 

  def response(self):
    return self._where().sort(self._sort()).limit(self._limit()).getInfo()

    # FeatureCollection.<filters>.<functions>.<sorts>.limit(n).getInfo()
    