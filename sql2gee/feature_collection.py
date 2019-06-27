import ee

from .collection import Collection


class FeatureCollection(Collection):
    """docstring for FeatureCollection"""

    def __init__(self, json, select, filters, asset_id, geometry=None):
        self.json = json
        self.select = select
        super().__init__(json['data']['attributes']['jsonSql'], select, filters, asset_id, 'FeatureCollection',
                         geometry)

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
        FeatureCollection.<filters>.<functions>.<sorts>.limit(n).getInfo()
        """
        return self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()
