from __future__ import print_function
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
        self._reducers = {
            'count': ee.Reducer.count(),
            'max': ee.Reducer.max(),
            'mean': ee.Reducer.mean(),
            'median': ee.Reducer.median(),
            'min': ee.Reducer.min(),
            'mode': ee.Reducer.mode(),
            'stdev': ee.Reducer.sampleStdDev(),
            'sum': ee.Reducer.sum(),
            'var': ee.Reducer.variance(),
        }

    @property
    def _is_image_request(self):
        """Boolean indication if the user intention is for an image (True) or Raster (False).
        Uses re package, to search _raw with A regex that splits on blank space, wildcards, and parentheses.
        Converts the lists to sets, and performs an intersect to see if Image-type keywords are present."""
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
        This is seperated from creating a formated table output (self.metadata).
        """
        if self._is_image_request:
            return ee.Image(self.target_data).getInfo()
        else:
            return None

    @cached_property
    def _band_names(self):
        if self._is_image_request:
            return ee.Image(self.target_data).bandNames().getInfo()
        else:
            return None

    @cached_property
    def _band_max(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['max'], bestEffort=True).getInfo()
        else:
            return None

    @cached_property
    def _band_means(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['mean'], bestEffort=True).getInfo()
        else:
            return None

    @cached_property
    def _band_min(self):
        if self._is_image_request:
            return ee.Image(self.target_data).reduceRegion(self._reducers['min'], bestEffort=True).getInfo()
        else:
            return None

    @property
    def metadata(self):
        """Formatted metadata"""
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
        else:
            return None

    @property
    def summary_stats(self):
        """Start of basic summary stat reporting for images"""
        if self._is_image_request:
            for b in self._band_names:
                print("Band = {0}, min = {1}, mean = {2}, max = {3}".format(
                    b, self._band_mins[b], self._band_means[b], self._band_maxs[b]))
        else:
            return None

    @property
    def _ee_image_histogram(self):
        """First step to retrieve ST_HISTOGRAM()-like info.
        This will return an object with the band-wise statistics for a reduced image. If no reduce (point + buffer)
        or polygon is given, we assume user wants all the possible image, in which case pass a default polygon to
        reduce on which is global. This raw data should then be parsed into useable info (including using it to derrive
        ST_SUMMARYSTATS()-like info).
        """
        # get max and min of band 1, and calculate bin number for histogram
        band_names = self._band_names
        band_maxs = self._band_max
        band_mins = self._band_min
        #self._band_names  # need to extract the max and min using the dictionary keys of band names
        # Find the largest/smallest max/min of all avaiable bands, and use this as input (and to calculate bin number)

        tmp_reducer = ee.Reducer.fixedHistogram(minval, maxval, 10)       # Identify reducer to apply to an image
        tmp_img = ee.Image(self.target_data)                        # Identify target data
        tmp_img.reduceRegion(reducer=tmp_reducer, bestEffort=True)  # Apply reducer
        #tmp_imp.getInfo()
        pass

    @property
    def gee_function(self):
        """The foundation object to construct the G.E.E. function from (i.e. an Image or a Feature Collection)."""
        if self._is_image_request:
            return self._image
        else:
            return self._feature_collection

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

    @property
    def _image(self):
        """Return the G.E.E. Image function with th the data, and relevant actions applied."""
        if self.image_action:
            pass
        return

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
        return fc

    @property
    def where(self):
        """Returns filter object obtained from where of the query in GEE format"""
        val, tmp = self._parsed.token_next_by(i=sqlparse.sql.Where)
        if tmp:
            return self.parse_conditions(tmp.tokens)
        return None

    @staticmethod
    def apply_group(fc, group):
        """Given a fc (feature_collection) object and group operation, return a
        new fc object, extended by a method of the feature grouping operation."""
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
        """Checks the first and last characters of an input_str
        to see if they are quotation marks [' or "], if so
        the function will strip them and return the string.
        :type input_str: str"""
        starts_with_quotation = input_str[0] in ['"', "'"]
        ends_with_quotation = input_str[-1] in ['"', "'"]
        if starts_with_quotation and ends_with_quotation:
            return input_str[1: -1]
        else:
            return input_str

    @staticmethod
    def token_to_dictionary(token_list):
        """Recieve a token e.g.('count(pepe)') and converts it into a dictionary
        with key:values for function and value."""
        assert isinstance(token_list, sqlparse.sql.Function),'unexpected datatype'
        d = {}
        for t in token_list:
            if isinstance(t, Identifier):
                d['function'] = str(t).upper()
            elif isinstance(t, Parenthesis):
                value = t.value.replace('(', '').replace(')', '').strip()
                if value != '*':
                    d['value'] = value
                else:
                    raise Exception('* not allowed')
        return d

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


    def execute(self):
        """Execute the GEE object in GEE Server. This is the function that, when called, actually sends the SQL
        request (which was converted to GEE-speak) to Google's servers for execution and returns the result."""
        ## This logic will be changed to instead execute the self.r , which will be made up of base + modifiers,
        # So it can be either and Image() or FeatureCollection() type function.
        if self._feature_collection:
            return self.gee_function.getInfo()
        return None
