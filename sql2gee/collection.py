import ee
from utils.reduce import _reducers

class Collection(object):
  """docstring for Collection"""
  def __init__(self, parsed, select, asset_id, dType, geometry=None):
    self._parsed = parsed
    self.select = select
    self.geometry = geometry
    self.type = dType
    self._asset_id = asset_id
    self._asset=self._assetInit() 
    self._filters = {
      '<': ee.Filter.lt,
      '<=': ee.Filter.lte,
      '>': ee.Filter.gt,
      '>=': ee.Filter.gte,
      '<>': ee.Filter.neq,
      '=': ee.Filter.eq,
      '!=': ee.Filter.neq,
      'bedate': ee.Filter.date,
      'between': ee.Filter.rangeContains,
      'like': ee.Filter.eq,
      '%like%': ee.Filter.stringContains,
      '%like': ee.Filter.stringEndsWith,
      'like%': ee.Filter.stringStartsWith
    }
    self._comparisons = {
      'and': ee.Filter.And,
      'or': ee.Filter.Or
    }
    self._agFunctions = {
      'avg': ee.Reducer.mean,
      'max': ee.Reducer.max,
      'min': ee.Reducer.min,
      'count': ee.Reducer.count,
      'sum': ee.Reducer.sum
      }

  def _assetInit(self):
    """
    Selects and retrieves the correct asset type
    """
    _data = {
      'FeatureCollection': ee.FeatureCollection,
      'ImageCollection': ee.ImageCollection
    }
    return _data[self.type](self._asset_id)

  def _filterGen(self, data, parents=[]):
    """
    Recursive function that will generate the proper filters that we will apply to the collections to filter them.
    Response like: ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])
    """
    left = None
    right = None
    result =[]
    dparents=list(parents)

    if 'type' in [*data] and data['type']=='conditional': ########---------------------------- Leaf with groups:
      left = data['left']
      right = data['right']
      dparents=[data['value']]
    elif 'type' in [*data] and data['type']=='operator': ########------------------------------------------- Latests leaf we will want to return  
      if data['right']['type']=='string':
        return self._filters[data['value']](data['left']['value'], data['right']['value'].strip("'"))
      else:
        return self._filters[data['value']](data['left']['value'], data['right']['value'])

    if left and right: ########-------------------------------------- leaf group iteration
      #for l in left:
      partialL=self._filterGen(left, dparents)
      #for r in right:
      partialR=self._filterGen(right, dparents)

      if not partialL:
        result=partialR
      elif not partialR:
        result=partialL
      else:
        result=self._comparisons[dparents[0]](partialR, partialL)
        #result={dparents[0] : [*partialR, *partialL]}

    return result ########----------------------------------- Return result in:[[ee.Filter.eq('month','historical'),ee.Filter.eq('model','historical'),...],...]
  
  def _where(self):
    """
    It gets *where* conditions and converts them in the proper filters.
    self.asset.filter(ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])).filterBounds(geometry)
    """
    
    if 'where' in self._parsed and self._parsed['where']:
      _filters=self._filterGen(self._parsed['where'])
      if self.geometry:
        self._asset = self._asset.filter(_filters).filterBounds(self.geometry)
      else:
        self._asset =  self._asset.filter(_filters)
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
      if isinstance(self._asset, ee.computedobject.ComputedObject):
        pass #### ToDo, should we implement an special algorithm for sortin to map the preresult dict 
      elif isinstance(self._asset, ee.Collection):
        self._asset = self._asset.sort(self._parsed['orderBy'][0]['value'], _direction[self._parsed['orderBy'][0]['direction']])
    
    return self

  def _limit(self):
    """
    This will limit  the answer if limit exist. 
    if the object is a collection it will use the built in function for it. 
    If instead the anwer is a dictionary, it will linit the output due the selected limit.
    """
    if 'limit' in self._parsed and self._parsed['limit']:
      if isinstance(self._asset, ee.computedobject.ComputedObject):
        self._asset=self._asset.slice(0, self._parsed['limit'])
      elif isinstance(self._asset, ee.Collection):
        self._asset = self._asset.limit(self._parsed['limit']).toList(self._parsed['limit'])
      else:
        raise type(self._asset)
    return self

  def _getInfo(self):
    return self._asset.getInfo()

  @property
  def reduceGen(self):
    groupBy = None
    if 'group' in self._parsed:
      groupBy = self._parsed['group']

    reducers = _reducers(self.select['_functions'], groupBy, self.geometry)
    
    return reducers

  
