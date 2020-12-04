import ee

from .collection import Collection
import logging 
logger = logging.getLogger(__name__)


class ImageCollection(Collection):
    """docstring for ImageCollection"""

    def __init__(self, json, select, filters, asset_id, geometry=None):
        self.json = json
        self.select = select
        super().__init__(json['data']['attributes']['jsonSql'], select, filters, asset_id, 'ImageCollection', geometry)

    def _initSelect(self):
        # For image collections select only affects bands and there is not a way of selecting also the columns/properties
        self._asset = self._asset.select(self.select['_bands'])
        return self

    def _initGroupsReducer(self, data, parents=[], proParents={}):
        keys = [*data]
        groups = None
        result = []
        dparents = list(parents)
        pparents = dict(proParents)
        if 'groups' in keys:  ########---------------------------- Leaf with groups:
            groups = data['groups']
            if (len(keys) > 1):  ########------------------------- If groups not alone:
                keys.remove('groups')
                dparents.append(ee.Filter.eq(keys[0], data[keys[0]]))
                pparents.update({keys[0]: data[keys[0]]})
        else:  ########------------------------------------------- Latests leaf we will want to return
            keys.remove('count')
            properties = dict(data)
            return {'filter': [ee.Filter.eq(keys[0], data[keys[0]]), *dparents],
                    'properties': {**{keys[0]: data[keys[0]]}, **pparents}}

        if groups:  ########-------------------------------------- leaf group iteration
            for group in groups:
                partialR = self._initGroupsReducer(group, dparents, pparents)
                ##----------------------------------------------- to keep it in a 2d array
                if isinstance(partialR, list):
                    result.extend(partialR)
                else:
                    result.append(partialR)
        return result  ########----------------------------------- Return result in: [{properties:{key: value},filters:[ee.Filter.eq('month','historical'),ee.Filter.eq('model','historical'),...]},...]

    def _collectionReducer(self):
        crossP = self._asset.reduceColumns(**self.reduceGen['reduceColumns'])
        mysubsets = self._initGroupsReducer(crossP.getInfo())
        del crossP
        if len(mysubsets) == self._asset.size().getInfo():
            # no need to reduce
            return self._asset
        else:
            collection = self._asset
            myList = ee.List([collection.filter(ee.Filter(filters['filter'])).reduce(
                **self.reduceGen['reduceImage']).setMulti(filters['properties']) for filters in mysubsets])
            return ee.ImageCollection(myList)

    def _ComputeReducer(self, img):
        reduction = img.reduceRegion(**self.reduceGen['reduceRegion'])
        properties = img.toDictionary(img.propertyNames()).combine(reduction)#.combine(img.toDictionary(['system:time_start', 'system:footprint', 'system:asset_size', 'system:index','time_start','time_end']))
        return ee.Feature(None, properties)

    def _groupBy(self):
        # To do discern between group by columns/bands; bands aren't allowed if not group by and global agg there
        if self.reduceGen['reduceImage'] and 'group' in self._parsed:
            reducedIColl = self._collectionReducer()
            self._asset = ee.FeatureCollection(reducedIColl.map(self._ComputeReducer))
        elif self.reduceGen['reduceImage']:
            reducedIColl = self._asset.reduce(**self.reduceGen['reduceImage'])
            self._asset = ee.FeatureCollection(self._ComputeReducer(ee.Image(reducedIColl)))

        return self

    def _mapOutputIList(self, image):
        output = self.calculate_output_format(image)
        output_alias = output['alias']
        if len(output_alias['result']) == 0:
            # image['properties']['system:id'] = image['id'] if 'id' in image.keys() else None
            image_dictionary = ee.Dictionary(image['properties'])
            return image_dictionary.select(output['output'], True).getInfo()

        if type(image) is dict:
            image['properties']['system:id'] = image['id'] if 'id' in image.keys() else None
            image_dictionary = ee.Dictionary(image['properties'])
            return image_dictionary.select(output['output'], True).rename(output_alias['result'], output_alias['alias']).getInfo()
        else:
            return image.select(output['output'], True).rename(output_alias['result'], output_alias['alias'])

    def response(self):
        """
        this will produce the following function chain in GEE:
        # ImageCollection.<filters>.<functions>.<sorts>.<imageReducers>.limit(n).getInfo()
        """
        result = self._initSelect()._where()._groupBy()._sort()._limit()._getInfo()
        logger.error(result)
        alias_mapped_results = [self._mapOutputIList(element) for element in result]

        return alias_mapped_results
