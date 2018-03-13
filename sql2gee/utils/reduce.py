import ee

def _group(reducer, groups):
  for group in groups:
      reducer = reducer.group(**group)
  return reducer

def _groupGen(groupBy, length):
    result = []
    for i, group in enumerate(groupBy, length):
        reducer = {'groupField': i,'groupName': group['value']}
        result.append(reducer)
        #if group == groupBy[-1]:
        #    result.append(reducer)
    return result

def _combineReducers(reducer, reducerFunctions):
    if len(reducerFunctions)==0:
        return reducer
    else:
        return _combineReducers(reducer.combine(reducerFunctions[0]), reducerFunctions[1:])

def _reduceImage(selectFunctions=None):
    reducers, selectors = _reducerGenerator(selectFunctions)
    if reducers:
        return {
          'reducer': reducers,
          'parallelScale': 10
          }
    else: 
        return None

def _reduceRegion(selectFunctions=None, geometry=None):
    reducers, selectors = _reducerGenerator(selectFunctions)
    if reducers and geometry:
        return {
          'reducer': reducers,
          'geometry': geometry,
          'bestEffort': True,
          'tileScale': 10,
          'scale': 90 
          } 
    else: 
        return None

def _reduceColumns(selectFunctions, groupBy=None):
    reducers, selectors = _reducerGenerator(selectFunctions, groupBy)
    
    if reducers and selectors:
        return {
          'reducer': reducers,
          'selectors': selectors
          }
    else: 
        return None

def _reducerGenerator(selectFunctions, groupBy=None):
    _agFunctions = {
    'avg': ee.Reducer.mean,
    'max': ee.Reducer.max,
    'min': ee.Reducer.min,
    'count': ee.Reducer.count,
    'sum': ee.Reducer.sum,
    'mode':ee.Reducer.mode,
    'st_histogram': ee.Reducer.autoHistogram,
    'distinct': ee.Reducer.countDistinct,
    'every': ee.Reducer.countEvery,
    'first': ee.Reducer.first,
    'last': ee.Reducer.last,
    'frequency': ee.Reducer.frequencyHistogram,
    'array_agg': ee.Reducer.toList
    
    }
    functionKeys = list(_agFunctions.keys())
    presentReducers = []
    reducerFunctions = []
    selectors = []
    
    for functionKey in functionKeys:
        if any(function['value'] == functionKey for function in selectFunctions):
            selectors.extend([function['arguments'][0]['value'] for function in selectFunctions if function['value'] == functionKey])
            quantity = sum(function['value'] == functionKey for function in selectFunctions)
            params=None
            reducer = _agFunctions[functionKey]().unweighted().repeat(quantity)
            presentReducers.append(_agFunctions[functionKey]())
            reducerFunctions.append(reducer)    
    
    # Reducers
    reducers=None
    if len(reducerFunctions) == 1:
        reducers = reducerFunctions[0]
    elif len(reducerFunctions) > 1:
        reducers = _combineReducers(reducerFunctions[0], reducerFunctions[1:])
    
    if groupBy != None:
        
        groups=_groupGen(groupBy, len(selectors))
        
        reducers = _group(reducers, groups)
    
    # selectors <only for reduce columns>
    if groupBy != None:       
        selectors.extend([group['value'] for group in groupBy])
    
    return reducers, selectors

def _reducers(selectFunctions, groupBy=None, geometry=None):
  if selectFunctions['columns'] == None and selectFunctions['bands'] and groupBy:
      selectFunctions['columns'] = [{'type': 'function', 
                                    'alias': None, 
                                    'value': 'count', 
                                    'arguments': [{'value': groupBy[0], 'type': 'literal'}]}]
  
  return {'reduceColumns': _reduceColumns(selectFunctions['columns'], groupBy),
          'reduceImage':_reduceImage(selectFunctions['bands']),
          'reduceRegion':_reduceRegion(selectFunctions['bands'], geometry)} ## result output