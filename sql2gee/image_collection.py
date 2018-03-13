import ee
import json
from collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, select, asset_id, geometry=None):
  	self.json = json
  	self.select = select
  	super().__init__(json['data']['attributes']['jsonSql'], select, asset_id, 'ImageCollection', geometry)
  
  def _initSelect(self):
  	# For image collections select only affects bands and there is not a way of selecting also the columns/properties
  	self._asset = self._asset.select(self.select['_bands'])
  	return self

  def _initGroupsReducer(self, data, parents=[]):
    keys=[*data]
    groups = None
    result =[]
    dparents=list(parents)
    if 'groups' in keys: ########---------------------------- Leaf with groups:
        groups = data['groups']
        if (len(keys) > 1): ########------------------------- If groups not alone:
            keys.remove('groups')
            dparents.append(ee.Filter.eq(keys[0],data[keys[0]]))
    else: ########------------------------------------------- Latests leaf we will want to return  
        keys.remove('count')
        return [ee.Filter.eq(keys[0],data[keys[0]]),*dparents]
    
    if groups: ########-------------------------------------- leaf group iteration
        for group in groups:
            partialR=self._initGroupsReducer(group, dparents)
            ##----------------------------------------------- to keep it in a 2d array
            if isinstance(partialR[0], list):
                result.extend(partialR)
            else:
                result.append(partialR)
    return result ########----------------------------------- Return result in:[[ee.Filter.eq('month','historical'),ee.Filter.eq('model','historical'),...],...] 

  def _collectionReducer(self):
    crossP = self._asset.reduceColumns(**self.reduceGen['reduceColumns'])
    mysubsets=_initGroupsReducer(crossP.getInfo())
    myList=ee.List([self._asset.reduce(**self.reduceGen['reduceImage']).set()  for filters in mysubsets])
    self._asset = ee.ImageCollection(myList)
    return self
  
  def _ComputeReducer(self, img):
    reduction = img.reduceRegion(**self.reduceGen['reduceRegion'])
    return ee.Feature(None, {
        'result': reduction,
        'system:time_start': img.get('system:time_start')
    })

  def _groupBy(self):	
    self._asset = ee.List(self._collectionReducer().map(ComputeReducer)).get('groups')	
    return self
  

  def response(self):
  	"""
	this will produce the next function in GEE:
	# ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo()
  	"""
  	print(self.select)
  	return self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()

  	
  	
    