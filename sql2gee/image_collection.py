from collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, select, asset_id, geometry):
  	self.json = json
  	self.select = select
  	super().__init__(json['data']['attributes']['jsonSql'], select, asset_id, 'ImageCollection', geometry)
  
  def _initSelect(self):
  	# For image collections select only affects bands and there is not a way of selecting also the columns/properties
  	self._asset = self._asset.select(self.select['_bands'])
  	return self

  def _aggFunctions(self):
    
    return self 
    
  def _groupBy(self):		
    return self
 
  def response(self):
  	"""
	this will produce the next function in GEE:
	# ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo().limit(1)
  	"""
  	print(self.select)
  	return self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()

  	
  	
    