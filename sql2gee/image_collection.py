from collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, select, asset_id, geometry):
  	self.json = json
  	super().__init__(json['data']['attributes']['jsonSql'], select, asset_id, 'ImageCollection', geometry)
  

  def _aggFunctions(self):
    
    return self 
    
  def _groupBy(self):		
    return self

  
  def query(self):
  	self._where()._groupBy()._sort()._limit()


  def response(self):
  	"""
	this will produce the next function in GEE:
	# ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo().limit(1)
  	"""
  	return self._where()._groupBy()._sort()._limit()._getInfo()

  	
  	
    