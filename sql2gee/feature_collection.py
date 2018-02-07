import ee
import json
from collection import Collection

ee.Initialize()

class FeatureCollection(Collection):
  """docstring for FeatureCollection"""
  def __init__(self, json, asset_id, geometry=None):
    self.json = json
    super().__init__(json['data']['attributes']['jsonSql'], asset_id, 'FeatureCollection', geometry)

  def _aggFunctions(self):
    
    return self
    
  def _groupBy(self):
    
    return self

  def response(self):
    
    return self._where()._groupBy()._sort()._limit()._getInfo()

    # FeatureCollection.<filters>.<functions>.<sorts>.limit(n).getInfo()
    