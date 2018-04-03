import ee
import json
from .collection import Collection

class ImageCollection(Collection):
  """docstring for ImageCollection"""
  def __init__(self, json, select, filters, asset_id, geometry=None):
  	self.json = json
  	self.select = select
  	super().__init__(json['data']['attributes']['jsonSql'], select, filters, asset_id, 'ImageCollection', geometry)
  
  def _initSelect(self):
  	# For image collections select only affects bands and there is not a way of selecting also the columns/properties
  	self._asset = self._asset.select(self.select['_bands'])
  	return self

  def _initGroupsReducer(self, data, parents=[],proParents={}):
    keys=[*data]
    groups = None
    result =[]
    dparents=list(parents)
    pparents=dict(proParents)
    if 'groups' in keys: ########---------------------------- Leaf with groups:
        groups = data['groups']
        if (len(keys) > 1): ########------------------------- If groups not alone:
            keys.remove('groups')
            dparents.append(ee.Filter.eq(keys[0],data[keys[0]]))
            pparents.update({keys[0]:data[keys[0]]})
    else: ########------------------------------------------- Latests leaf we will want to return  
        keys.remove('count')
        properties = dict(data)
        return {'filter':[ee.Filter.eq(keys[0],data[keys[0]]),*dparents], 'properties': {**{keys[0]:data[keys[0]]},**pparents}}
    
    if groups: ########-------------------------------------- leaf group iteration
        for group in groups:
            partialR=self._initGroupsReducer(group, dparents, pparents)
            ##----------------------------------------------- to keep it in a 2d array
            if isinstance(partialR, list):
                result.extend(partialR)
            else:
                result.append(partialR)
    return result ########----------------------------------- Return result in: [{properties:{key: value},filters:[ee.Filter.eq('month','historical'),ee.Filter.eq('model','historical'),...]},...]

  def _collectionReducer(self):
    crossP = self._asset.reduceColumns(**self.reduceGen['reduceColumns'])
    mysubsets=self._initGroupsReducer(crossP.getInfo())
    collection = self._asset
    myList=ee.List([collection.filter(ee.Filter(filters['filter'])).reduce(**self.reduceGen['reduceImage']).setMulti(filters['properties'])  for filters in mysubsets])
    return  ee.ImageCollection(myList)
  
  def _ComputeReducer(self, img):
    reduction = img.reduceRegion(**self.reduceGen['reduceRegion'])
    return ee.Feature(None, img.toDictionary().combine(reduction))
    

  def _groupBy(self):
    #To do discern between group by columns/bands; bands aren't allowed if not group by and global agg there, 
    if self.reduceGen['reduceImage'] and 'group' in self._parsed:
      
      reducedIColl = self._collectionReducer()
      self._asset = reducedIColl.map(self._ComputeReducer).toList(999999)
    elif self.reduceGen['reduceImage']:
      reducedIColl = self._asset.reduce(**self.reduceGen['reduceImage']) 
      self._asset = ee.FeatureCollection(self._ComputeReducer(ee.Image(reducedIColl)))

    return self
  

  def response(self):
    """
    this will produce the next function in GEE:
    # ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo()
    """
    return self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()

  	
  	
    