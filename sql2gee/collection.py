import ee
from cached_property import cached_property
from .utils.reduce import _reducers
import functools

class Collection(object):
  """docstring for Collection"""
  def __init__(self, parsed, select, filters, asset_id, dType, geometry=None):
    self._parsed = parsed
    self._filters = filters
    self.select = select
    self.type = dType
    self._asset_id = asset_id
    self._asset=self._assetInit()
    self.geometry = self._geometry(geometry)

  def _assetInit(self):
    """
    Selects and retrieves the correct asset type
    """
    _data = {
      'FeatureCollection': ee.FeatureCollection,
      'ImageCollection': ee.ImageCollection
    }
    return _data[self.type](self._asset_id)
  
  def _geometry(self, geometry):
    if geometry or self.type=='FeatureCollection':
      return geometry
    else:
      return self._asset.geometry()
      
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
  
  @cached_property 
  def _output(self):
    """return dict output and alias arrays ordered"""
    _Output = {
    "output":[],
    "alias":{
      "result":[],
      "alias":[]
      },
    }
    n_func = len(set([f['value'] for f in self.select['_functions']['bands'] ]))
    n_reduc = len(list(filter(None, self.reduceGen.values())))
    n_times = n_reduc if n_func > 1 else 1
    #Funcion management
    for function in self.select['functions']:
      #the way GEE constructs the function values is <band/column>_<function(RImage/RColumn)>_<function(RRegion)>
      
      for args in function['arguments']:
        if args['type']=='literal' and args['value'] in self.select['_columns'] or args['value'] in self.select['_bands']:
          functionValue = 'mean' if function['value'] == 'avg' else function['value']
          functionName = '{0}_{1}'.format(args['value'],'_'.join([functionValue for x in range(0, n_times)]))
          
          _Output["output"].append(functionName)
          if function['alias']:
            _Output["alias"]["result"].append(functionName)
            _Output["alias"]["alias"].append(function['alias'])


    #columns management
    for column in self.select['columns']:
      _Output["output"].append(column['value'])
      
      if column['alias']:
        _Output["alias"]["result"].append(column['value'])
        _Output["alias"]["alias"].append(column['alias'])
    return _Output

  @staticmethod
  def _mapOutputIList(img):
    if len(output['alias']['result'])>0:
      return ee.Image(img).toDictionary(output['output']).rename(output['alias']['result'], output['alias']['alias'])
    elif len(output["output"])>0:
      return ee.Image(img).toDictionary(output['output'])
    else:
      return ee.Image(img).toDictionary()
  
  @staticmethod
  def _mapOutputFList(feat):
    print(output["output"])
    if len(output['alias']['result'])>0:
      return ee.Feature(feat).toDictionary(output['output']).rename(output['alias']['result'], output['alias']['alias'])
    elif len(output["output"])>0:
      return ee.Feature(feat).toDictionary(output['output'])
    else:
      return ee.Feature(feat).toDictionary()


  #def _mapOutputList(self):
    """mapping to get the output columns, aliases and normalize the output"""
   

  def _limit(self):
    """
    This will limit  the answer if limit exist. 
    if the object is a collection it will use the built in function for it. 
    If instead the anwer is a dictionary, it will linit the output due the selected limit.
    """
    
    global output; output = self._output
    print(self._asset.getInfo())
    if 'limit' in self._parsed and self._parsed['limit']:
      if isinstance(self._asset, ee.ee_list.List):
        self._asset=self._asset.slice(0, self._parsed['limit'])
      elif isinstance(self._asset, ee.imagecollection.ImageCollection):
        self._asset = self._asset.toList(self._parsed['limit']).map(self._mapOutputIList)
      elif isinstance(self._asset, ee.featurecollection.FeatureCollection):
        self._asset = self._asset.toList(self._parsed['limit']).map(self._mapOutputFList)
      else:
        raise type(self._asset)
    elif isinstance(self._asset, ee.imagecollection.ImageCollection):
      ##Lets limit the output: TODO Paginate it
      self._asset = self._asset.toList(10000).map(self._mapOutputIList)
    elif isinstance(self._asset, ee.featurecollection.FeatureCollection):
      ##Lets limit the output: TODO Paginate itf
      self._asset = self._asset.toList(10000).map(self._mapOutputFList)
      #elf._asset = ee.List(self._asset.toList(10000).map(functools.partial(test_f, output=self._output)))
    #elif isinstance(self._asset, ee.ee_list.List):
      ##Lets limit the output: TODO Paginate it
      #self._asset = self._asset.map()
    
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

