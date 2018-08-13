import ee

def _group(reducer, groups):
  """
  Description here
  """
  for group in groups:
      reducer = reducer.group(**group)
  return reducer

def _groupGen(groupBy, length):
  """
  Description here
  """
  result = []
  for i, group in enumerate(groupBy, length):
      reducer = {'groupField': i,'groupName': group['value']}
      result.append(reducer)
      
  return result

def _combineReducers(reducer, reducerFunctions, sharedIn=False):
  """
  Description here
  """
  if len(reducerFunctions)==0:
    return reducer
  else:
    return _combineReducers(reducer.combine(reducerFunctions[0], sharedInputs=sharedIn), reducerFunctions[1:])

def _reduceImage(selectFunctions=None):
  """
  Description here
  """
  reducers, selectors = _reducerGenerator(selectFunctions, None, 'image')
  if reducers:
      return {
        'reducer': reducers,
        'parallelScale': 10
        }
  else: 
      return None

def _reduceRegion(selectFunctions=None, geometry=None, scale=90):
  """
  Description here
  """
  reducers, selectors = _reducerGenerator(selectFunctions, None, 'image')
  if reducers and geometry:
      return {
        'reducer': reducers,
        'geometry': geometry,
        'scale': scale,
        'bestEffort': True,
        'maxPixels':9e8,
        'tileScale': 16
        
        } 
  else: 
      return None

def _reduceColumns(selectFunctions, groupBy=None):
  """
  Description here
  """
  reducers, selectors = _reducerGenerator(selectFunctions, groupBy)
  
  if reducers and selectors:
      return {
        'reducer': reducers,
        'selectors': selectors
        }
  else: 
      return None

def _reducerGenerator(selectFunctions, groupBy=None, reducerFor='column'):
  """
  Description here
  """
  _agFunctions = {
  'avg': ee.Reducer.mean,
  'mean': ee.Reducer.mean,
  'max': ee.Reducer.max,
  'min': ee.Reducer.min,
  'var': ee.Reducer.variance,
  'stdev': ee.Reducer.stdDev,
  'count': ee.Reducer.count,
  'sum': ee.Reducer.sum,
  'mode':ee.Reducer.mode,
  'st_histogram': ee.Reducer.autoHistogram,
  'st_valuecount': ee.Reducer.frequencyHistogram,
  'every': ee.Reducer.countEvery,
  'first': ee.Reducer.first,
  'last': ee.Reducer.last,
  'frequency': ee.Reducer.frequencyHistogram,
  'array_agg': ee.Reducer.toList
  }
  functionKeys = list(_agFunctions.keys())
  reducerFunctions = []
  selectors = []
  # Reducers
  for functionKey in functionKeys:
      if any(function['value'].lower() == functionKey for function in selectFunctions):
          selectors.extend([function['arguments'][0]['value'] for function in selectFunctions if function['value'].lower() == functionKey])
          quantity = sum(function['value'].lower() == functionKey for function in selectFunctions)
          params=None ## For reducer that require params (in the future)
          
          if reducerFor == 'column':
            ##### Complex reduction to apply to Columns
            reducer = _agFunctions[functionKey]().unweighted().repeat(quantity)
          elif reducerFor == 'image':
            ##### reduction to apply to Images
            reducer = _agFunctions[functionKey]()
          else: 
            raise 
          
          reducerFunctions.append(reducer) 
          
  
  reducers=None
  if len(reducerFunctions) == 1:
      reducers = reducerFunctions[0]
  elif len(reducerFunctions) > 1:
      if reducerFor == 'column':
        reducers = _combineReducers(reducerFunctions[0], reducerFunctions[1:])
      elif reducerFor == 'image':
        reducers = _combineReducers(reducerFunctions[0], reducerFunctions[1:], True)
  
  if groupBy != None:
      # selectors <only for reduce columns>
      groups=_groupGen(groupBy, len(selectors))
      reducers = _group(reducers, groups)
      selectors.extend([group['value'] for group in groupBy])    
   
  return reducers, selectors

def _reducers(selectFunctions, groupBy=None, geometry=None):
  functions=dict(selectFunctions)
  if len(functions['columns']) == 0 and len(functions['bands'])>0 and groupBy!=None:
    functions['columns'] = [{'type': 'function', 
                                  'alias': None, 
                                  'value': 'count', 
                                  'arguments': [groupBy[0]]}]
  
  return {'reduceColumns': _reduceColumns(functions['columns'], groupBy),
          'reduceImage':_reduceImage(functions['bands']),
          'reduceRegion':_reduceRegion(functions['bands'], geometry)} ## result output