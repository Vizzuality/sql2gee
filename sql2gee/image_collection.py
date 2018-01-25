from collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, asset_id):
    self.json = json
    self.asset_id = asset_id
    self._parsed = json['data']['attributes']['jsonSql']
    Collection.__init__(self, self._parsed, self.asset_id, 'FeatureCollection')
    
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

    # ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo()