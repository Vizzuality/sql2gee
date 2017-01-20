from __future__ import print_function, division
from cached_property import cached_property
import ee
import re
import sqlparse
from sqlparse.tokens import Keyword
from sqlparse.sql import Identifier, IdentifierList, Function, Parenthesis, Comparison


class SQL2GEE(object):
    """
    Takes an SQL-like query and relates it to Google's Earth Engine syntax (specifically the Python 2.7 GEE API).
    Designed to perform operations on two types of geo-objects, Polygons (Feature Collections) or Rasters (Images).
    For the rasters there are only a specific number of valid operations (retrieve metadata, histogram data, or get
    summary statistics). We use postgis-like functions as the syntax to do this, and check to see if this is given in
    the sql string to detect the user intention.

    If geojson data is provided, we will assume that a user intends for us to subset an image, by these data.
    """
    def __init__(self, sql, geojson=None, flags=None):
        self._raw = sql
        self._parsed = sqlparse.parse(sql)[0]
        self.geojson = self._geojson_to_featurecollection(geojson)
        self.flags = flags  # <-- Will be used in a later version of the code
        self._filters = {
            '<': ee.Filter().lt,
            '<=': ee.Filter().lte,
            '>': ee.Filter().gt,
            '>=': ee.Filter().gte,
            '<>': ee.Filter().neq,
            '=': ee.Filter().eq,
            '%LIKE%': ee.Filter().stringContains,
            '%LIKE': ee.Filter().stringEndsWith,
            'LIKE%': ee.Filter().stringStartsWith,
            'LIKE': ee.Filter().eq,
        }
        self._comparisons = {
            'AND': ee.Filter().And,
            'OR': ee.Filter().Or
        }

    def _geojson_to_featurecollection(self, geojson):
        """If Geojson kwarg is recieved (containing geojson data) convert it into a useable E.E. object."""
        if isinstance(geojson, dict):
            assert geojson.get("geojson").get('features') != None, "Expected key not found in item passed to geojoson"
            ee_geoms = []
            for feature in geojson.get("geojson").get('features'):
                feature_type = feature.get("geometry").get('type').lower()
                if feature_type == 'multipolygon':
                    tmp = ee.Geometry.MultiPolygon(feature.get('geometry').get('coordinates'))
                    ee_geoms.append(tmp)
                else:
                    tmp = ee.Geometry.Polygon(feature.get('geometry').get('coordinates'))
                    ee_geoms.append(tmp)
            return ee.FeatureCollection(ee_geoms)
        else:
            return None

    @property
    def _is_image_request(self):
        """Detect if the user intends to use an image (True) or Feature collection (False). In the future a flag will
        be used to do this."""
        tmp = [r for r in re.split('[\(\*\)\s]', self._raw.lower()) if r != '']
        tmp = set(tmp)
        image_keywords = {'st_histogram', 'st_metadata', 'st_summarystats'}
        intersect = tmp.intersection(image_keywords)
        if len(intersect) == 0:
            return False
        elif len(intersect) == 1:
            return True
        else:
            raise ValueError("Found multiple image-type keywords. Unsure of action.")

    @cached_property
    def _band_names(self):
        if self._is_image_request:
            return ee.Image(self.target_data).bandNames().getInfo()

    @cached_property
    def _reduce_image(self):
        """ Construct a combined reducer dictionary and pass it to a ReduceRegion().getInfo() command.
        If a geometry has been passed to SQL2GEE, it will be passed to ensure only a subset of the band is examined.
        """
        d={}
        d['bestEffort'] = True
        if self.geojson:
            d['geometry'] = self.geojson
        d['reducer'] = ee.Reducer.count().combine(ee.Reducer.sum(), outputPrefix='', sharedInputs=True
                        ).combine(ee.Reducer.mean(), outputPrefix='', sharedInputs=True).combine(
                        ee.Reducer.sampleStdDev(), outputPrefix='', sharedInputs=True).combine(ee.Reducer.min(),
                        outputPrefix='', sharedInputs=True).combine(ee.Reducer.max(), outputPrefix='',
                        sharedInputs=True).combine(ee.Reducer.percentile([25, 75]), outputPrefix='', sharedInputs=True)
        return ee.Image(self.target_data).reduceRegion(**d).getInfo()

    @cached_property
    def _band_IQR(self):
        """Return a dictionary object with the InterQuartileRange (Q3 - Q1) per band."""
        if self._is_image_request:
            iqr = {}
            for band in self._band_names:
                tmp = self._reduce_image[band + '_p75'] - self._reduce_image[band + '_p25']
                iqr[band] = tmp
                del tmp
            return iqr

    @cached_property
    def metadata(self):
        """Property that holds the Metadata dictionary returned from Earth Engine."""
        if self._is_image_request:
            return ee.Image(self.target_data).getInfo()

    @cached_property
    def summary_stats(self):
        """Return a dictionary object of summary stats like the postgis function ST_SUMMARYSTATS()."""
        d = {}
        for band in self._band_names:
            d[band] = {'count': self._reduce_image[band+'_count'],
                       'sum': self._reduce_image[band+'_sum'],
                       'mean': self._reduce_image[band+'_mean'],
                       'stdev':self._reduce_image[band+'_stdDev'],
                       'min': self._reduce_image[band+'_min'],
                       'max': self._reduce_image[band+'_max']
                       }
        return d

    @cached_property
    def histogram(self):
        """Retrieve ST_HISTOGRAM()-like info.
        This will return a dictionary object with bands as keys, and for each band a nested list of (2xn) for bin and frequency
        e.g.: {['band1']: [[left-bin position, frequency] ... n-bins]]}
        """
        # Estimate optimum bin width and bin number with Freedman-Diaconis method
        first_band_max = self._reduce_image[self._band_names[0]+'_max']
        first_band_min = self._reduce_image[self._band_names[0]+'_min']
        first_band_iqr = self._band_IQR[self._band_names[0]]
        first_band_n = self._reduce_image[self._band_names[0]+'_count']
        bin_width = (2 * first_band_iqr * (first_band_n ** (-1/3)))
        num_bins = int((first_band_max - first_band_min) / bin_width)
        d = {}
        d['reducer'] = ee.Reducer.fixedHistogram(first_band_min, first_band_max, num_bins)
        d['bestEffort'] = True
        if self.geojson:
            d['geometry'] = self.geojson
        return ee.Image(self.target_data).reduceRegion(**d).getInfo()

    def _histplot_preview(self):
        """Returns a matplotlib plot object, meant for development previews only.
        This needs numpy and matplotlib to be installed, which are not included in the requirements for size.
        sql = "SELECT ST_HISTPLOT() FROM srtm90_v4"
        r = SQL2GEE(sql)
        r._histplot_preview()
        """
        import numpy as np
        import matplotlib.pyplot as plt
        for key in self.histogram:
            if self.histogram[key]:
                bins = []
                frequency = []
                for item in self.histogram[key]:
                    bin_left, val = item
                    bins.append(bin_left)
                    frequency.append(val)
                bins = np.array(bins)
                frequency = np.array(frequency)
                counts = [self._reduce_image[band+'_count'] for band in self._band_names]
                counts = np.array(counts)
                plt.step(bins, frequency / counts)
                plt.title(key.capitalize())
                plt.ylabel("frequency")
                if plt:
                    plt.show()
        return

    @property
    def target_data(self):
        """Set target_data property using sql tokens, assuming it
        is the first token of type Identifier after the 'FROM' keyword
        also of type Identifier. If not found, raise an Exception."""
        from_seen = False
        exception_1 = Exception('Dataset not found')
        for item in self._parsed.tokens:
            if from_seen:
                if isinstance(item, Identifier):
                    return self.remove_quotes(str(item))
                elif item.ttype is Keyword:
                    raise exception_1
            elif item.ttype is Keyword and str(item).upper() == 'FROM':
                from_seen = True
        raise exception_1

    @property
    def fields(self):
        """A list of all fields in SQL query. If the FROM keyword is
        encountered the list is immediately returned.
        """
        field_list = []
        for t in self._parsed.tokens:
            is_keyword = t.ttype is Keyword
            is_from = str(t).upper() == 'FROM'
            if is_keyword and is_from:
                return field_list
            elif isinstance(t, Identifier):
                field_list.append(str(t))
            elif isinstance(t, IdentifierList):
                for identity in t.tokens:
                    if isinstance(identity, Identifier):
                        field_list.append(str(identity))
        return field_list

    @property
    def group_functions(self):
        """Returns the group function with column names specified in the query:
        e.g. from sql input of 'select count(pepe) from mytable', a dictionary of
        {'function': 'COUNT', 'value': 'pepe'} should be returned by self.group_functions"""
        group_list = []
        for t in self._parsed.tokens:
            if t.ttype is Keyword and t.value.upper() == 'FROM':
                return group_list
            elif isinstance(t, Function):
                group_list.append(self.token_to_dictionary(t))
            elif isinstance(t, IdentifierList):
                for identity in t.tokens:
                    if isinstance(identity, Function):
                        group_list.append(self.token_to_dictionary(identity))
        return group_list

    @staticmethod
    def token_to_dictionary(token_list):
        """ Receives a token e.g.('count(pepe)') and converts it into a dict
        with key:values for function and value ."""
        assert isinstance(token_list, sqlparse.sql.Function),'unexpected datatype'
        d = {}
        for t in token_list:
            if isinstance(t, Identifier):
                d['function'] = str(t).upper()
            elif isinstance(t, Parenthesis):
                value = t.value.replace('(', '').replace(')', '').strip()
                d['value'] = value
        return d

    @property
    def _image(self):
        """Performs a diffrent Image operation depending on sql request."""
        if self._is_image_request:
            for func in self.group_functions:
                subset = func["value"].lower()
                st_histogram_requested = func["function"].lower() == 'st_histogram'
                st_summarystats_requested = func["function"].lower() == 'st_summarystats'
                st_metadata_requested = func["function"].lower() == 'st_metadata'
                if st_histogram_requested:
                    return self.histogram
                if st_metadata_requested:
                    return self.metadata
                if st_summarystats_requested:
                    return self.summary_stats

    @property
    def _feature_collection(self):
        """Return the G.E.E. FeatureCollection object with all filter, groups, and functions applied"""
        fc = ee.FeatureCollection(self.target_data)
        if self.where:
            fc = fc.filter(self.where)
        if self.group_functions:
            for group in self.group_functions:
                fc = self.apply_group(fc, group)
        select = self.fields
        if select and len(select) > 0 and not select[0] == '*':
            fc = fc.select(select)
        if self.limit:
            fc = fc.limit(self.limit)
        return fc

    @property
    def where(self):
        """Returns filter object obtained from where of the query in GEE format"""
        val, tmp = self._parsed.token_next_by(i=sqlparse.sql.Where)
        if tmp:
            return self.parse_conditions(tmp.tokens)
        return None

    @property
    def limit(self):
        """If LIMIT keyword set, this returns an integer to limit the maximum return from a feature collection query"""
        watch_for_limit = False
        for i in list(self._parsed):
            if i.ttype is Keyword and i.value.lower() == "LIMIT".lower():
                watch_for_limit = True
            if watch_for_limit and i.ttype is sqlparse.tokens.Literal.Number.Integer:
                limit_value = int(i.value)
                assert limit_value >= 1, 'Limit must be >= 1'
                return limit_value

    def apply_group(self, fc, group):
        """Given a fc (feature_collection) object and group operation, return a
        new fc object, extended by a method of the feature grouping operation."""
        if not self._is_image_request:
            if group['function'] == 'COUNT':
                return fc.aggregate_count(group['value'])
            elif group['function'] == 'MAX':
                return fc.aggregate_max(group['value'])
            elif group['function'] == 'MIN':
                return fc.aggregate_min(group['value'])
            elif group['function'] == 'SUM':
                return fc.aggregate_sum(group['value'])
            elif group['function'] == 'AVG':
                return fc.aggregate_mean(group['value'])
            elif group['function'] == 'FIRST':
                return fc.aggregate_first(group['value'])
            elif group['function'] == 'LAST':
                return fc.aggregate_last(group['value'])
            else:
                raise ValueError("Unknown group function attempted: ", group['function'])

    @staticmethod
    def remove_quotes(input_str):
        """Checks the first and last characters of an input_str to see if they are quotation marks [' or "], if so
        the function will strip them and return the string.
        :type input_str: str"""
        starts_with_quotation = input_str[0] in ['"', "'"]
        ends_with_quotation = input_str[-1] in ['"', "'"]
        if starts_with_quotation and ends_with_quotation:
            return input_str[1: -1]
        else:
            return input_str

    def parse_comparison(self, comparison):
        values = []
        comparator = None
        for item in comparison.tokens:
            if isinstance(item, Identifier):
                values.append(self.remove_quotes(item.value))
            elif item.ttype is sqlparse.tokens.Comparison:
                comparator = item.value
            elif not item.is_whitespace:
                if item.ttype is sqlparse.tokens.Number.Integer:
                    values.append(int(item.value))
                elif item.ttype is sqlparse.tokens.Number.Float:
                    values.append(float(item.value))
                else:
                    values.append(self.remove_quotes(item.value))
        if comparator:
            return self._filters[comparator](values[0], values[1])

    def generate_like(self, left, comp, right, exist_not):
        if comp.value.upper() == 'LIKE':
            filter = None
            if right.strip().startswith('%') and right.strip().endswith('%'):
                filter = self._filters['%' + comp.value.upper() + '%'](left, right[1:len(right) - 1])
            elif right.strip().startswith('%'):
                filter = self._filters['%' + comp.value.upper()](left, right[1:len(right)])
            elif right.strip().endswith('%'):
                filter = self._filters[comp.value.upper() + '%'](left, right[0:len(right) - 1])
            else:
                filter = self._filters[comp.value.upper()](left, right)

            if exist_not:
                return filter.Not()
            return filter
        else:
            raise Exception(comp.value + ' not supported')

    def generate_in(self, left, comp, right, exist_not):
        filter = ee.Filter().inList(left, right)
        if exist_not:
            return filter.Not()
        return filter

    def generate_is(self, left, comp, right, ):
        if right.upper() == 'NULL':
            return ee.Filter().eq(left, 'null')
        elif right.upper().startswith('NOT') and right.upper().endswith('NULL'):
            return ee.Filter().neq(left, 'null')
        else:
            raise Exception('IS only support NULL value')

    def parse_list(self, tokens):
        values = []
        for item in tokens:
            if isinstance(item, Identifier):
                values.append(self.remove_quotes(item.value))
            elif not item.is_whitespace and item.value != ',':
                if item.ttype is sqlparse.tokens.Number.Integer:
                    values.append(int(item.value))
                elif item.ttype is sqlparse.tokens.Number.Float:
                    values.append(float(item.value))
                else:
                    values.append(self.remove_quotes(item.value))
        return values

    def parse_conditions(self, tokens):
        filters = []
        comparison = None
        sub_comparison = None
        leftValue = None
        exist_not = False
        for item in tokens:
            if isinstance(item, Comparison):
                filter = self.parse_comparison(item)
                if exist_not:
                    filter = filter.Not()
                filters.append(filter)
            elif item.ttype is Keyword and (item.value.upper() == 'AND' or item.value.upper() == 'OR'):
                comparison = self._comparisons[item.value.upper()]
            elif isinstance(item, Parenthesis):
                filter = self.parse_conditions(item.tokens)
                if isinstance(filter, ee.Filter):
                    filters.append(filter)
                elif type(filter) is list:
                    filters.append(self.generate_in(leftValue, sub_comparison, filter, exist_not))
                    leftValue = None
                    sub_comparison = None
                    exist_not = False
            elif item.ttype is Keyword and (item.value.upper() == 'LIKE' or item.value.upper() == 'IN' or item.value.upper() == 'IS'):
                sub_comparison = item
            elif item.ttype is Keyword and item.value.upper() == 'NOT':
                exist_not = True
            elif isinstance(item, IdentifierList):
                return self.parse_list(item.tokens)
            elif item.ttype is None or (item.ttype is Keyword and (item.value.upper() == 'NULL' or item.value.upper().startswith('NOT'))):
                if leftValue is None:
                    leftValue = item.value
                else:
                    if sub_comparison.value.upper() == 'LIKE':
                        filters.append(self.generate_like(leftValue, sub_comparison, self.remove_quotes(item.value), exist_not))
                    elif sub_comparison.value.upper() == 'IS':
                        filters.append(self.generate_is(leftValue, sub_comparison, self.remove_quotes(item.value)))
                    sub_comparison = None
                    leftValue = None
                    exist_not = False
            if comparison and len(filters) == 2:
                statement = comparison(filters[0], filters[1])
                if exist_not:
                    statement = statement.Not()
                    exist_not = False
                filters = [statement]
                comparison = None
        return filters[0]

    @property
    def response(self):
        """Execute the GEE object in GEE Server. This is the function that, when called, actually sends the SQL
        request (which was converted to GEE-speak) to Google's servers for execution and returns the result."""
        ## This logic will be changed to instead execute the self.r , which will be made up of base + modifiers,
        # So it can be either and Image() or FeatureCollection() type function.
        if self._feature_collection:
            try:
                return self._feature_collection.getInfo()
            except:
                raise AttributeError('Failed to return Feature Collection result')
        if self._image:
            try:
                return self._image
            except:
                raise AttributeError("Failed to return Image result")
