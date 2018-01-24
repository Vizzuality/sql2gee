import ee

ee.Initialize()

class Collection(object):
  """docstring for Collection"""
  def __init__(self, parsed, asset_id, type, geojson=None):
    super(Collection, self).__init__()
    self._parsed = parsed
    self.geojson = geojson
    self.type = type
    self._asset_id = asset_id
    self._asset =self._getAsset()
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
      'min': ee.Reducer.min,
    }

  def _getAsset(self):
    _data = {
      'FeatureCollection':ee.FeatureCollection(self._asset_id),
      'ImageCollection':ee.ImageCollection(self._asset_id)
    }

    return _data[self.type]

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
  
  def _where(self):
    # It gets *where* conditions and converts them in the proper filters.
    # self.asset.filter(ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])).filterBounds(geometry)
    _filters=self._filterGen(self._parsed['where'])

    if self.geojson:
      return self._asset.filter(_filters).filterBounds(self.geojson)
    else:
      return self._asset.filter(_filters)

    return 0

  def _sort(self):
    return self._parsed['orderBy'][0]['value']

    # sort_params = self._parsed['orderBy'][0]

    # return {
    #   'direction': sort_params['direction'],
    #   'value': sort_params['value']
    # }

  def _limit(self):
    return self._parsed['limit']
