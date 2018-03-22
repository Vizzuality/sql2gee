import ee
from cached_property import cached_property
from .utils.reduce import _reducers

class Collection(object):
  """docstring for Collection"""
  def __init__(self, parsed, select, filters, asset_id, dType, geometry=None):
    self._parsed = parsed
    self._filters = filters
    self.select = select
    self.geometry = geometry
    self.type = dType
    self._asset_id = asset_id
    self._asset=self._assetInit() 

  def _assetInit(self):
    """
    Selects and retrieves the correct asset type
    """
    _data = {
      'FeatureCollection': ee.FeatureCollection,
      'ImageCollection': ee.ImageCollection
    }
    return _data[self.type](self._asset_id)
  
  def _where(self):
    """
    It gets *where* conditions and converts them in the proper filters.
    self.asset.filter(ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])).filterBounds(geometry)
    """
    
    if 'where' in self._parsed and self._parsed['where']:
      if self.geometry:
        self._asset = self._asset.filter(self._filters['filter']).filterBounds(self.geometry)
      else:
        self._asset =  self._asset.filter(self._filters['filter'])
    return self

  def _sort(self):
    """
    This will sort the result over the first condition as gee doesn't allow multisort
    """
    _direction={
    'asc':True,
    'desc':False
    }
    if 'orderBy' in self._parsed and self._parsed['orderBy']:
      if isinstance(self._asset, ee.ee_list.List):
        pass #### ToDo, should we implement an special algorithm for sortin to map the preresult dict 
      elif isinstance(self._asset, ee.imagecollection.ImageCollection) or isinstance(self._asset, ee.featurecollection.FeatureCollection):
        for order in  self._parsed['orderBy']:
          self._asset = self._asset.sort(order['value'], _direction[order['direction']])
    
    return self

  def _limit(self):
    """
    This will limit  the answer if limit exist. 
    if the object is a collection it will use the built in function for it. 
    If instead the anwer is a dictionary, it will linit the output due the selected limit.
    """
    if 'limit' in self._parsed and self._parsed['limit']:
      if isinstance(self._asset, ee.ee_list.List):
        self._asset=self._asset.slice(0, self._parsed['limit'])
      elif isinstance(self._asset, ee.imagecollection.ImageCollection) or isinstance(self._asset, ee.featurecollection.FeatureCollection):
        self._asset = self._asset.toList(self._parsed['limit'])
      else:
        raise type(self._asset)
    elif isinstance(self._asset, ee.imagecollection.ImageCollection) or isinstance(self._asset, ee.featurecollection.FeatureCollection):
      ##Lets limit the output: TODO Paginate it
      self._asset = self._asset.toList(10000)
    
    return self

  def _getInfo(self):
    """docstring for Collection"""
    return self._asset.getInfo()

  @cached_property 
  def reduceGen(self):
    groupBy = None
    if 'group' in self._parsed:
      groupBy = self._parsed['group']

    reducers = _reducers(self.select['_functions'], groupBy, self.geometry)
    
    return reducers

