import json
import logging

import ee
from cached_property import cached_property

from .utils.reduce import _reducers

logger = logging.getLogger(__name__)


class Collection(object):
    """docstring for Collection"""

    def __init__(self, parsed, select, filters, asset_id, dType, geometry=None):
        self._parsed = parsed
        self._filters = filters
        self.select = select
        self.type = dType
        self._asset_id = asset_id
        self._asset = self._assetInit()
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
        if geometry:
            return geometry
        return ee.FeatureCollection(json.loads(
            '{"type": "FeatureCollection","features":[{"type":"Feature", "properties": {}, "geometry": {"type":"Polygon", "coordinates": [[[-180,-90],[180,-90],[180,90],[-180,90],[-180,-90]]]}}]}').get(
            'features'))

    def _where(self):
        """
        It gets *where* conditions and converts them in the proper filters.
        self.asset.filter(ee.Filter([ee.Filter.eq('scenario','historical'), ee.Filter.date('1996-01-01','1997-01-01')])).filterBounds(geometry)
        """
        if 'where' not in self._parsed or len(self._parsed['where']) == 0:
            return self

        if 'filter' in self._filters:
            self._asset = self._asset.filter(self._filters['filter'])

        if self.geometry:
            self._asset = self._asset.filterBounds(self.geometry)

        return self

    def _sort(self):
        """
        This will sort the result over the first condition as gee doesn't allow multisort
        """
        _direction = {
            'asc': True,
            'desc': False
        }
        if 'orderBy' in self._parsed and self._parsed['orderBy']:
            if isinstance(self._asset, ee.ee_list.List):
                pass  #### ToDo, should we implement an special algorithm for sortin to map the preresult dict
            elif isinstance(self._asset, ee.imagecollection.ImageCollection) or isinstance(self._asset,
                                                                                           ee.featurecollection.FeatureCollection):
                for order in self._parsed['orderBy']:
                    self._asset = self._asset.sort(order['value'], _direction[order['direction']])

        return self

    def calculate_output_format(self, value):
        """return dict output and alias arrays ordered"""
        _Output = {
            "output": [],
            "alias": {
                "result": [],
                "alias": []
            },
        }
        n_func = len(set([f['value'] for f in self.select['_functions']['bands']]))

        # Function management
        for function in self.select['functions']:
            # the way GEE constructs the function values is <band/column>_<function(RImage/RColumn)>_<function(RRegion)>

            for args in function['arguments']:
                if args['type'] == 'literal' and args['value'] in self.select['_columns'] or args['value'] in \
                        self.select['_bands']:
                    functionValue = 'mean' if function['value'] == 'avg' else function['value']
                    for iterations in range(0, n_func + 2):
                        temp_subname = '_'.join([functionValue for x in range(0, iterations)])
                        temp_name = '{0}{1}'.format(args['value'],
                                                    f"_{temp_subname}" if temp_subname else '')
                        if 'properties' in value and temp_name in value['properties']:
                            functionName = temp_name
                            _Output["output"].append(functionName)
                            if function['alias']:
                                _Output["alias"]["result"].append(functionName)
                                _Output["alias"]["alias"].append(function['alias'])

                            break
                    # if functionName is None:
                    #     raise Exception('Error: cannot calculate output format for column {}'.format(args['value']))

        # columns management
        for column in self.select['columns']:
            _Output["output"].append(column['value'])

            if column['alias']:
                _Output["alias"]["result"].append(column['value'])
                _Output["alias"]["alias"].append(column['alias'])
        return _Output

    def _mapOutputFList(self, feat):
        output = self.calculate_output_format()

        if len(output['alias']['result']) > 0:
            return ee.Feature(feat).toDictionary(output['output']).rename(output['alias']['result'],
                                                                          output['alias']['alias'])
        elif len(output["output"]) > 0:
            return ee.Feature(feat).toDictionary(output['output'])
        else:
            return ee.Feature(feat).toDictionary()

    def _limit(self):
        """
        This will limit  the answer if limit exist.
        if the object is a collection it will use the built in function for it.
        If instead the answer is a dictionary, it will limit the output due the selected limit.
        """

        if 'limit' in self._parsed and self._parsed['limit']:
            if isinstance(self._asset, ee.ee_list.List):
                self._asset = self._asset.slice(0, self._parsed['limit'])
            elif isinstance(self._asset, ee.imagecollection.ImageCollection):
                self._asset = self._asset.toList(self._parsed['limit'])
            elif isinstance(self._asset, ee.featurecollection.FeatureCollection):
                self._asset = self._asset.toList(self._parsed['limit'])
            else:
                raise type(self._asset)
        elif isinstance(self._asset, ee.imagecollection.ImageCollection):
            ##Lets limit the output: TODO Paginate it
            self._asset = self._asset.toList(10000)
        elif isinstance(self._asset, ee.featurecollection.FeatureCollection):
            ##Lets limit the output: TODO Paginate itf
            # self._asset = self._asset.toList(10000).map(self._mapOutputFList)
            self._asset = self._asset.toList(10000)
            # elf._asset = ee.List(self._asset.toList(10000).map(functools.partial(test_f, output=self._output)))
        # elif isinstance(self._asset, ee.ee_list.List):
        ##Lets limit the output: TODO Paginate it
        # self._asset = self._asset.map()

        return self

    def _getInfo(self):
        """docstring for Collection"""
        return self._asset.getInfo()

    @cached_property
    def reduceGen(self):
        group_by = None
        if 'group' in self._parsed:
            group_by = self._parsed['group']

        reducers = _reducers(self.select['_functions'], group_by, self.geometry)

        return reducers
