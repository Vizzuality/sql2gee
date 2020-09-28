import json

import ee
from cached_property import cached_property

from .feature_collection import FeatureCollection
from .image import Image
from .image_collection import ImageCollection


class GeeFactory(object):
    """docstring for GeeFactory"""

    def __init__(self, sql_scheme, geojson=None, flags=None):
        """
        Description here
        """
        self.json = sql_scheme
        self._parsed = self.json['data']['attributes']['jsonSql']
        self.sql = self.json['data']['attributes']['query']
        self._asset_id = self.json['data']['attributes']['jsonSql']['from'].strip("'").strip('"')
        self.type = self.metadata['type']
        self.geojson = geojson
        self.flags = flags  # <-- Will be used in a later version of the code

    def _geo_extraction(self, json_input):
        """
        Description here
        """
        lookup_key = 'type'
        lookup_value = 'function'
        sql_function = 'ST_GeomFromGeoJSON'
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key and v == lookup_value and json_input['value'] == sql_function:
                    yield json_input['arguments'][0]['value'].strip("'")
                else:
                    for child_val in self._geo_extraction(v):
                        yield child_val
        elif isinstance(json_input, list):
            for item in json_input:
                for item_val in self._geo_extraction(item):
                    yield item_val

    def _geojson_to_featurecollection(self, geojson):
        """If Geojson kwarg is received or ST_GEOMFROMGEOJSON sql argument is used,
        (convert it into a usable E.E. object.obtaining geojson data) c"""

        geometries = [json.loads(x) for x in self._geo_extraction(self._parsed)]

        if geometries:
            geojson = {
                "features": geometries,
                "type": "FeatureCollection"
            }
        if isinstance(geojson, dict):
            assert geojson.get('features') is not None, "Expected key not found in item passed to geojoson"
            return ee.FeatureCollection(geojson.get('features'))
        else:
            return None

    @cached_property
    def metadata(self):
        """Property that holds the Metadata dictionary returned from Earth Engine."""
        if 'ft:' in self._asset_id:
            meta = ee.FeatureCollection(self._asset_id).limit(0).getInfo()
            assert meta is not None, 'please enter a valid fusion table'

            info = {
                'type': meta['type'],
                'columns': meta['columns'],
                'id': self._asset_id,
                'version': '',
                'properties': meta['properties']
            }

            return info
        else:
            info = ee.data.getAsset(self._asset_id)

            assert info is not None, "data type not expected"

            # if ('bands' in info) and (not info['bands']):
            if info['type'] == 'IMAGE_COLLECTION':
                meta = ee.ImageCollection(self._asset_id).limit(1).getInfo()['features'][0]
                info['bands'] = meta['bands']
                info['columns'] = {k: type(v).__name__ for k, v in meta['properties'].items()}

        return info

    @cached_property
    def _initSelect(self):
        """
        Description
        """
        info = {}

        ## This will store the bands and properties separately if they exist in the asset
        if 'columns' in self.metadata and self.metadata['columns']:
            info['_init_cols'] = self.metadata['columns'].keys()
        if 'bands' in self.metadata and self.metadata['bands']:
            info['_init_bands'] = [v['id'] for v in self.metadata['bands']]
        elif self.type == 'TABLE' or self.type == 'FEATURE_COLLECTION':
            info['_init_cols'] = ee.FeatureCollection(self.metadata['id']).limit(1).getInfo()['columns']

        return info

    def _findDup(self, list):
        r = [i for n, i in enumerate(list) if i not in list[n + 1:]]
        return len(list) == len(r)

    def _filterGen(self, data, parents=[]):
        """
        Recursive function that will generate the proper filters that we will apply to the collections to filter them.
        Response like: ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])
        """
        _filters = {
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
        _comparisons = {
            'and': ee.Filter.And,
            'or': ee.Filter.Or
        }
        left = None
        right = None
        result = []
        dparents = list(parents)

        if 'type' in [*data] and data['type'] == 'conditional':
            ########---------------------------- Leaf with groups:
            left = data['left']
            right = data['right']
            dparents = [data['value']]

        elif 'type' in [*data] and data['type'] == 'operator':
            ########------------------------------------------- Latests leaf we will want to return. we will need to check if it is a band or a column.
            if data['left'][0]['value'] in self._initSelect['_init_cols']:
                if 'time' in data['left'][0]['value'] and data['right'][0]['type'] in ['string', 'date']:
                    ########------------------------------------------- Date management at filter level this is TEMPORAL TODO until we do have a proper way of identify it.
                    data['right'][0]['value'] = ee.Date.parse('dd-mm-yyyy',
                                                              data['right'][0]['value'].strip("'")).millis()
                    data['right'][0]['type'] = 'date'
                if data['right'][0]['type'] == 'string':
                    return {'column': [data['left'][0]['value']],
                            'filter': _filters[data['value']](data['left'][0]['value'],
                                                              data['right'][0]['value'].strip("'"))}
                else:
                    return {'column': [data['left'][0]['value']],
                            'filter': _filters[data['value']](data['left'][0]['value'], data['right'][0]['value'])}
            elif data['left']['value'] in self._initSelect['_init_bands']:
                # todo think what to do with bands in filter where
                raise Exception('error; non supported operation: filter by column ', data['left'][0]['value'])
            else:
                raise Exception('error; nonexisting column: ', data['left'][0]['value'])

        if left and right:  ########-------------------------------------- leaf group iteration
            # for l in left:
            partialL = self._filterGen(left[0], dparents)

            # for r in right:
            partialR = self._filterGen(right[0], dparents)

            if not partialL:
                result = partialR

            elif not partialR:
                result = partialL
            else:
                result = {'column': list(set([*partialR['column'], *partialL['column']])),
                          'filter': _comparisons[dparents[0]](partialR['filter'], partialL['filter'])}

        return result  ########----------------------------------- Return result in:[[ee.Filter.eq('month','historical'),ee.Filter.eq('model','historical'),...],...]

    @cached_property
    def _filter(self):
        if 'where' in self._parsed:
            return self._filterGen(self._parsed['where'][0])
        else:
            return None

    @cached_property
    def _select(self):
        """
        This will receive the select statement of the query and transform it in the way we need it
        """
        selectArray = self.json['data']['attributes']['jsonSql']['select']
        selected = {
            '_init_cols': [],
            '_init_bands': []
        }
        response = {
            'columns': [],
            '_columns': [],
            'bands': [],
            '_bands': [],
            'functions': [],
            '_functions': {
                'bands': [],
                'columns': []
            },
            'others': []
        }
        info = self._initSelect

        # Compare the select results with the available columns/bands
        for selectElement in selectArray:
            # This will retrieve the columns and bands inside select and check if the names belong to those in the data
            if selectElement['type'] == 'literal':
                if '_init_cols' in info and selectElement['value'] in info['_init_cols']:
                    response['columns'].append(selectElement)
                elif '_init_bands' in info and selectElement['value'] in info['_init_bands']:
                    response['bands'].append(selectElement)
                else:
                    raise NameError('column/band name not valid: {0}'.format(selectElement['value']))

            # This will retrieve the columns and bands for our dataset and extend the cols/bands to select if they already hasn't being selected
            elif selectElement['type'] == 'function':
                response['functions'].append(selectElement)
                # This will divide the functions that are related bands from those related columns so we can use the in the reducers.
                if '_init_cols' in info:
                    # this will test if the arguments contains a column and if so it will added it to our select tree
                    if any(args['type'] == 'literal' and args['value'] in info['_init_cols'] for args in
                           selectElement['arguments']):
                        response['_functions']['columns'].append(selectElement)
                    selected['_init_cols'].extend([args['value'] for args in selectElement['arguments'] if
                                                   args['type'] == 'literal' and args['value'] in info['_init_cols']])

                if '_init_bands' in info:
                    # this will test if the arguments contains a band and if so it will added it to our select tree
                    if any(args['type'] == 'literal' and (
                            args['value'] in info['_init_bands'] or args['value'] in ['rast']) for args in
                           selectElement['arguments']):
                        response['_functions']['bands'].append(selectElement)
                    selected['_init_bands'].extend([args['value'] for args in selectElement['arguments'] if
                                                    args['type'] == 'literal' and args['value'] in info['_init_bands']])

                if '_init_bands' in info and '_init_cols' in info:
                    f = [args['value'] for args in selectElement['arguments'] if
                         args['type'] == 'literal' and args['value'] not in info['_init_bands'] and args['value'] not in
                         info['_init_cols']]

                elif '_init_bands' in info:
                    f = [args['value'] for args in selectElement['arguments'] if
                         args['type'] == 'literal' and args['value'] not in info['_init_bands']]

                elif '_init_cols' in info:
                    f = [args['value'] for args in selectElement['arguments'] if
                         args['type'] == 'literal' and args['value'] not in info['_init_cols'] and args['value']]

                if f and len(f) == len(selectElement['arguments']) and 'rast' not in f:
                    raise NameError('column/band name not valid in function {0}: {1}'.format(selectElement['value'], f))

            elif selectElement['type'] == 'wildcard':
                if '_init_cols' in info and len(info['_init_cols']) > 0:
                    d = [{'type': 'literal', 'alias': None, 'value': f} for f in info['_init_cols']]
                    response['columns'].extend(d)
                elif '_init_bands' in info and len(info['_init_bands']) > 0:
                    d = [{'type': 'literal', 'alias': None, 'value': f} for f in info['_init_bands']]
                    response['bands'].extend(d)

            else:
                response['others'].append(selectElement)

        for key, value in response.items():
            if key in ['columns', 'bands']:
                assert self._findDup(value), 'we cannot have 2 columns with the same alias'.format()

        if self._filter:
            response['_columns'] = list(
                set([a['value'] for a in response['columns']]).union(selected['_init_cols']).union(
                    self._filter['column']))
        else:
            response['_columns'] = list(set([a['value'] for a in response['columns']]).union(selected['_init_cols']))

        response['_bands'] = list(set([a['value'] for a in response['bands']]).union(selected['_init_bands']))

        return response

    def response(self):
        """
        Description here
        """
        geom = self._geojson_to_featurecollection(self.geojson)

        if self.type == 'IMAGE':
            return Image(self.sql, self.json, self._select, self._filter, self._asset_id, self.metadata, geom).response()
        elif self.type == 'IMAGE_COLLECTION':
            return ImageCollection(self.json, self._select, self._filter, self._asset_id, geom).response()
        elif self.type == 'FEATURE_COLLECTION' or self.type == 'TABLE':
            return FeatureCollection(self.json, self._select, self._filter, self._asset_id, geom).response()
        else:
            raise Exception('Invalid type {}'.format(self.type))

