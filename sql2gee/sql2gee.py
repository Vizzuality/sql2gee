from __future__ import print_function, division
import numpy as np
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
    """
    def __init__(self, sql):
        self._raw = sql
        self._parsed = sqlparse.parse(sql)[0]
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

    @property
    def _reducers(self):
        """Due to an E.E. initialization quirk, the reducers must be created after the __init__ stage"""
        d = {
            'count': ee.Reducer.count(),
            'max': ee.Reducer.max(),
            'mean': ee.Reducer.mean(),
            'median': ee.Reducer.median(),
            'min': ee.Reducer.min(),
            'mode': ee.Reducer.mode(),
            'percentiles': ee.Reducer.percentile([25, 50, 75]),
            'stdev': ee.Reducer.sampleStdDev(),
            'sum': ee.Reducer.sum(),
            'var': ee.Reducer.variance()
        }
        return d

    @property
    def _is_image_request(self):
        """Detect if the user intends to use an image (True) or Feature collection (False)"""
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
    def _ee_image_metadata(self):
        """Private property that holds the raw EE image(target).get_info() function.
        This is separated from creating a formatted table output (self.metadata).
        """
        if self._is_image_request:
            return ee.Image(self.target_data).getInfo()

    # NOTE : it is in the below reducers, that I should add a conditional to subset by a feature/feature collection
    # if they are provided in the sql query rather than the current default of None...

    @cached_property
    def _band_names(self):
        if self._is_image_request:
            return ee.Image(self.target_data).bandNames().getInfo()

    @cached_property
    def _band_max(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['max'], bestEffort=True).getInfo()

    @cached_property
    def _band_mean(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['mean'], bestEffort=True).getInfo()

    @cached_property
    def _band_min(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['min'], bestEffort=True).getInfo()

    @cached_property
    def _band_percentiles(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['percentiles'], bestEffort=True).getInfo()

    @cached_property
    def _band_counts(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['count'], bestEffort=True).getInfo()

    @cached_property
    def _band_IQR(self):
        """Return a dictionary object with the InterQuartileRange (Q3 - Q1) per band."""
        if self._is_image_request:
            iqr = {}
            for band in self._band_names:
                tmp = self._band_percentiles[band + '_p75'] - self._band_percentiles[band + '_p25']
                iqr[band] = tmp
                del tmp
            return iqr

    def metadata(self, subset=None):
        """Formatted metadata"""
        if len(subset) > 0:
            print('Subset requested: ', subset)
        if self._ee_image_metadata:
            meta = self._ee_image_metadata # request metadata from G.E.E
            for n, band in enumerate(meta['bands']):
                print("-- Band {0} --".format(n))
                print("CRS: ", band['crs'])
                print("Transform: ", band['crs_transform'])
                print("Data type: ", band['data_type']["type"])
                print("ID: ", band['id'])
                print("Pixel Dimensions: ", band['dimensions'])
                print("Min value: ", band['data_type']['min'])
                print("Max value: ", band['data_type']['max'])
            return


    def summary_stats(self, subset=None):
        """Start of basic summary stat reporting for images to be exposed to the users, ST_SUMMARYSTATS()-like."""
        if len(subset) > 0:
            print("Subset requested:", subset)
        for b in self._band_names:
            print("Band = {0}, min = {1}, mean = {2}, max = {3}".format(
                b, self._band_min[b], self._band_mean[b], self._band_max[b]))


    def histogram(self, subset=None):
        """This property is responsible for modifying the raw output of E.E. histogram dictionary into a
        PostGIS-like output."""
        if len(subset) > 0:
            print("Subset requested: ", subset)
        return self._ee_image_histogram

    # step 1 : see if gemeotry data is passed - could be passsed with ST_CLIP or
    # type could be geostore, geojson, or fusiontable
    # step 2: ensure it is a feature collection (if not make it one)
    # step 3: pass it to the fixedHistogramReducer


    @property
    def _ee_image_histogram(self):
        """First step to retrieve ST_HISTOGRAM()-like info.
        This will return an object with the band-wise statistics for a reduced image. If no reduce (point + buffer)
        or polygon is given, we assume user wants all the possible image, in which case pass a default polygon to
        reduce on which is global. This raw data should then be parsed into usable info (including using it to derive
        ST_SUMMARYSTATS()-like info).

        First step is to reduce with global data, but, will add polygons/ point+buffers. In this case the statistics
        for the bands (max, min, counts, range, iqr, n) also need to come from the feature, not the whole band....
        """
        # Estimate optimum bin width and bin number with Freedman-Diaconis method
        first_band_max = self._band_max[self._band_names[0]]
        first_band_min = self._band_min[self._band_names[0]]
        first_band_iqr = self._band_IQR[self._band_names[0]]
        first_band_n = self._band_counts[self._band_names[0]]
        bin_width = (2 * first_band_iqr * (first_band_n ** (-1/3)))
        num_bins = np.round((first_band_max - first_band_min) / bin_width)
        # Set-up a histogram reducer, pass it to an image, and return the histogram data dictionary.
        tmp_reducer = ee.Reducer.fixedHistogram(first_band_min, first_band_max, num_bins)
        tmp = ee.Image(self.target_data).reduceRegion(reducer=tmp_reducer, bestEffort=True).getInfo()
        return tmp


    def _histplot_preview(self):
        """Returns a matplotlib plot object, meant for development previews only.

        sql = "SELECT ST_METADATA(*) FROM srtm90_v4"
        r = SQL2GEE(sql)
        p = r._histplot_preview()
        p.show()
        """
        import matplotlib.pyplot as plt
        for key in self._ee_image_histogram:
            if self._ee_image_histogram[key]:
                bins = []
                frequency = []
                for item in self._ee_image_histogram[key]:
                    bin_left, val = item
                    bins.append(bin_left)
                    frequency.append(val)
                bins = np.array(bins)
                frequency = np.array(frequency)
                plt.step(bins, frequency / self._band_counts[key])
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
                    return self.histogram(subset=subset)
                if st_metadata_requested:
                    return self.metadata(subset=subset)
                if st_summarystats_requested:
                    return self.summary_stats(subset=subset)

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
