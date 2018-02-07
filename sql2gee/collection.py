import ee

ee.Initialize()

class Collection(object):
  """docstring for Collection"""
  def __init__(self, parsed, asset_id, dType, geometry=None):
    self._parsed = parsed
    self.geometry = geometry
    self.type = dType
    self._asset_id = asset_id
    self._asset=self._asset()
    
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
      'mean': ee.Reducer.mean,
      'max': ee.Reducer.max,
      'min': ee.Reducer.min,
      'count': ee.Reducer.count,
    }
    self._agTFunctions = {
      'mean': ee.Reducer.mean,
      'max': ee.Reducer.max,
      'min': ee.Reducer.min,
      'min': ee.Reducer.count,
    }

  def _filterGen(self, data, parents=[]):
    left = None
    right = None
    result =[]
    dparents=list(parents)

    if 'type' in [*data] and data['type']=='conditional': ########---------------------------- Leaf with groups:
      left = data['left']
      right = data['right']
      dparents=[data['value']]
    elif 'type' in [*data] and data['type']=='operator': ########------------------------------------------- Latests leaf we will want to return  
      return self._filters[data['value']](data['left']['value'], data['right']['value'])
      #return {data['value']:[data['left']['value'], data['right']['value']]}

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
  
  def _asset(self):
    _data = {
      'FeatureCollection': ee.FeatureCollection,
      'ImageCollection': ee.ImageCollection
    }
    return _data[self.type](self._asset_id)
  
  
  def _where(self):
    # It gets *where* conditions and converts them in the proper filters.
    # self.asset.filter(ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])).filterBounds(geometry)
    
    if self._parsed['where']:
      _filters=self._filterGen(self._parsed['where'])
      if self.geometry:
        self._asset = self._asset.filter(_filters).filterBounds(self.geometry)
      else:
        self._asset =  self._asset.filter(_filters)
    return self
   

  
  def _sort(self):
    _direction={
    'asc':True,
    'desc':False
    }
    if self._parsed['orderBy']:
      self._asset = self._asset.sort(self._parsed['orderBy'][0]['value'], _direction[self._parsed['orderBy'][0]['direction']])
    
    return self
    
    

  def _limit(self):
    if self._parsed['limit']:
      self._asset = self._asset.limit(self._parsed['limit'])
    return self

  def _getInfo(self):
    return self._asset.getInfo()

