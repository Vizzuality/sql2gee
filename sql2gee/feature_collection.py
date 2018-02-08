import ee
import json
from collection import Collection

ee.Initialize()

class FeatureCollection(Collection):
  """docstring for FeatureCollection"""
  def __init__(self, json, select, asset_id, geometry=None):
    self.json = json
    self.select = select
    super().__init__(json['data']['attributes']['jsonSql'], select, asset_id, 'FeatureCollection', geometry)

  def _initSelect(self):
    self._asset = self._asset.select(self.select['_columns'])
    return self

  def _aggFunctions(self):
    
    return self
    
  def _groupBy(self):
    
    return self

  def response(self):
    
    return self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()

    # FeatureCollection.<filters>.<functions>.<sorts>.limit(n).getInfo()
    