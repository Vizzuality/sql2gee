import ee
import json
from image import Image
#from json_sql import JsonSql
from image_collection import ImageCollection
from feature_collection import FeatureCollection

ee.Initialize()

class GeeFactory(object):

  """docstring for GeeFactory"""
  def __init__(self, sqlscheme, geojson=None, flags=None):
    self.json = sqlscheme
    self._parsed = self.json['data']['attributes']['jsonSql']
    self.sql = self.json['data']['attributes']['query']
    self._asset_id = self.json['data']['attributes']['jsonSql']['from'].strip("'")
    self.type = self.metadata['type']
    self.geojson = geojson 
    self.flags = flags  # <-- Will be used in a later version of the code

  def _geo_extraction(self, json_input):
    lookup_key = 'type'
    lookup_value = 'function'
    Sqlfunction = 'ST_GeomFromGeoJSON'

    if isinstance(json_input, dict):
      for k, v in json_input.items():
        if k == lookup_key and v == lookup_value and json_input['value'] == Sqlfunction:
          yield json_input['arguments'][0]['value'].strip("'")
        else:
          for child_val in self._geo_extraction(v):
            yield child_val
    elif isinstance(json_input, list):
      for item in json_input:
        for item_val in self._geo_extraction(item):
          yield item_val

  def _geojson_to_featurecollection(self, geojson):
    """If Geojson kwarg is recieved or ST_GEOMFROMGEOJSON sql argument is used,
    (convert it into a useable E.E. object.ontaining geojson data) c"""
    geometries = [json.loads(x) for x in self._geo_extraction(self._parsed)]

    if geometries:
      geojson = {
        u'features': geometries,
        u'type': u'FeatureCollection'
      }

    if isinstance(geojson, dict):
      assert geojson.get('features') != None, "Expected key not found in item passed to geojoson"
      return ee.FeatureCollection(geojson.get('features'))
    else:
      return None
  @property
  def metadata(self):
    """Property that holds the Metadata dictionary returned from Earth Engine."""
    if 'ft:' in self._asset_id:
      meta = ee.FeatureCollection(self._asset_id).limit(0).getInfo()
      assert meta != None, 'please enter a valid fusion table'

      info = {
        'type': meta['type'],
        'columns':meta['columns'],
        'id':self._asset_id,
        'version':'',
        'properties':meta['properties']
      }

      return info
    else:
      info = ee.data.getInfo(self._asset_id)
      assert info != None, "data type not expected"

      if ('bands' in info) and (not info['bands']):
        meta = ee.ImageCollection(self._asset_id).limit(1).getInfo()['features'][0] ### this is a bit ... 
        info['bands'] = meta['bands']
        info['columns'] = { k: type(v).__name__  for k,v in meta['properties'].items()}
              
    return info
    
  def _findDup(self, list):
    r = [i for n, i in enumerate(list) if i not in list[n + 1:]]
    return len(list) == len(r)

  @property  
  def _select(self):
    """
    This will recive the select statment of the query and transform it in the way we need it 
    """
    selectArray = self.json['data']['attributes']['jsonSql']['select']

    selected={
    '_init_cols':[],
    '_init_bands':[]
    }
    response={
        'columns':[],
        '_columns':[],
        'bands':[],
        '_bands':[],
        'functions':[],
        'others':[]
    }
    info={}

    ## This will store the bands and columns separately if they exist in the asset
    if 'columns' in self.metadata and self.metadata['columns']:
      info['_init_cols']=self.metadata['columns'].keys()
    if 'bands' in self.metadata and self.metadata['bands']:
      info['_init_bands']=[v['id'] for v in self.metadata['bands']]

    #Compare the select results with the available columns/bands
    for a in selectArray:
        if a['type']=='literal':
            # This will retrieve the columns and bands inside select and check if the names belong to those in the data
            if '_init_cols' in info and a['value'] in info['_init_cols']:
                response['columns'].append(a)
            elif '_init_bands' in info and a['value'] in info['_init_bands']:
                response['bands'].append(a)
            else:
                raise NameError('column/band name not valid: {0}'.format(a['value']))
            
        elif a['type']=='function':
            # This will retrieve the columns and bands for our dataset and extend the cols/bands to select if they already hasn't being selected
            response['functions'].append(a)
            if '_init_cols' in info:
              selected['_init_cols'].extend([args['value'] for args in a['arguments'] if args['type']=='literal' and args['value'] in info['_init_cols']])
            if '_init_bands' in info:
              selected['_init_bands'].extend([args['value'] for args in a['arguments'] if args['type']=='literal'and args['value'] in info['_init_bands']])
            if '_init_bands' in info and '_init_cols' in info:
              f = [args['value'] for args in a['arguments'] if args['type']=='literal'and args['value'] not in info['_init_bands'] and args['value'] not in info['_init_cols']]
            elif '_init_bands' in info:
              f = [args['value'] for args in a['arguments'] if args['type']=='literal' and args['value'] not in info['_init_bands']]
            elif '_init_cols' in info:
              f = [args['value'] for args in a['arguments'] if args['type']=='literal' and  args['value'] not in info['_init_cols'] and args['value']]


            if f and len(f)==len(a['arguments']):
                raise NameError('column/band name not valid in function {0}: {1}'.format(a['value'],f))
        
        elif a['type']=='wildcard':
            d = [{'type':'literal','alias': None, 'value':f} for f in info['_init_cols']]
            response['columns'].extend(d)
        
        else:
            response['others'].append(a)
    
    for key, value in response.items():
      if key in ['columns','bands']:
        assert self._findDup(value), 'we cannot have 2 columns with the same alias'.format()
    
    response['_columns'] =list(set([a['value'] for a in response['columns']]).union(selected['_init_cols']))
    response['_bands']=list(set([a['value'] for a in response['bands']]).union(selected['_init_bands']))
    
    return response
    


  def response(self):
    _default_geojson = json.loads('{"features": [{"geometry": {"coordinates": [[[-90, -180],[-90, -180], [-90, -180 ], [-90, -180], [-90, -180]]], "geodesic":true, "type":"Polygon"}, "type": "Feature"} ], "type": "FeatureCollection"}')
    imGeom = self.geojson if self.geojson else _default_geojson # To avoid the image composite bug we add a global region to group the image together.
    collGeom = self._geojson_to_featurecollection(self.geojson)
    
    fnResponse={
    'Image': Image(self.sql, self.json, self._select, self._asset_id, imGeom).response,
    'ImageCollection': ImageCollection(self.json, self._select, self._asset_id, collGeom).response,
    'FeatureCollection': FeatureCollection(self.json, self._select, self._asset_id, collGeom).response
    }
    
    try:
      return fnResponse[self.type]()
    except ee.EEException:
        # raise Error
        print('GEEFactory Exception: ')
        raise
        
    
