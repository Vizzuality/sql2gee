import ee

from .collection import Collection


class FeatureCollection(Collection):
    """docstring for FeatureCollection"""

    def __init__(self, json, select, filters, asset_id, geometry=None):
        self.json = json
        self.select = select
        super().__init__(json['data']['attributes']['jsonSql'], select, filters, asset_id, 'FeatureCollection',
                         geometry)

    def _mapOutputFList(self, feat):
        if len(self._output['alias']['result']) > 0:
            return feat.rename(self._output['alias']['result'], self._output['alias']['alias'])
        # elif len(self._output["output"]) > 0:
        #     return ee.Feature(feat).toDictionary(self._output['output'])
        else:
            return feat

    def _initSelect(self):
        self._asset = self._asset.select(self.select['_columns'])
        return self

    def _groupBy(self):
        """ data = feature collection
            select = list with column id you want to count/sum
            aggFunctions =aggregation functions
            groups = list containing the columns you wish to group by,
                        starting with the coarse grouping, ending with fine grouping"""
        if self.reduceGen['reduceColumns']:
            if 'group' in self._parsed:
                self._asset = ee.List(self._asset.reduceColumns(**self.reduceGen['reduceColumns']).get('groups'))
            else:
                self._asset = ee.List([self._asset.reduceColumns(**self.reduceGen['reduceColumns'])])

        return self

    def response(self):
        """
        this will produce the following function chain in GEE:
        # FeatureCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo()
        """
        result = self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()
        alias_mapped_results = [self._mapOutputFList(element) for element in result]

        return alias_mapped_results
