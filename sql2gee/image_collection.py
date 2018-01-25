from collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, asset_id):
    self.json = json
    self.asset_id = asset_id
    self._parsed = json['data']['attributes']['jsonSql']
    Collection.__init__(self, self._parsed, self.asset_id, 'FeatureCollection')
    
  def response(self):
  	return self._where().sort(self._sort()[0],self._sort()[1]).limit(self._limit()).getInfo()

    # ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo().limit(1)