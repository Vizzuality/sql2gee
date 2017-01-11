import sqlparse
import ee
from sqlparse.tokens import Keyword, Comparison
from sqlparse.sql import Identifier, IdentifierList, Function, Parenthesis, Comparison


class SQL2GEE:
    def __init__(self, sql):
        """Intialize the object and parse sql. Return SQL2GEE object to do the process"""
        self.parsed = sqlparse.parse(sql)[0]
        self.filters = {
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
        self.comparisons = {
            'AND': ee.Filter().And,
            'OR': ee.Filter().Or
        }

    @property
    def table_name(self):
        """Set table_name property using sql tokens, assuming it
        is the first token of type Identifier after the 'FROM' keyword
        also of type Identifier. If not found, raise an Exception."""
        from_seen = False
        exception_1 = Exception('Table name not found')
        for item in self.parsed.tokens:
            if from_seen:
                if isinstance(item, Identifier):
                    return self.remove_quotes(str(item))
                elif item.ttype is Keyword:
                    raise exception_1
            elif item.ttype is Keyword and str(item).upper() == 'FROM':
                from_seen = True
        raise exception_1

    def get_select_list(self):
        """Return list with the columns specified in the query"""
        list = []
        for item in self.parsed.tokens:
            if item.ttype is Keyword and item.value.upper() == 'FROM':
                return list
            elif isinstance(item, Identifier):
                list.append(item.value)
            elif isinstance(item, IdentifierList):
                for ident in item.tokens:
                    if isinstance(ident, Identifier):
                        list.append(ident.value)
        return list

    def parse_group(self, token_list):
        token = {}
        for item in token_list:
            if isinstance(item, Identifier):
                token['function'] = item.value.upper()
            elif isinstance(item, Parenthesis):
                value = item.value.replace('(', '').replace(')', '').strip()
                if value != '*':
                    token['value'] = value
                else:
                    raise Exception('* not allowed')
        return token

    def get_group_functions(self):
        """Returns the group function with column names specified in the query"""
        list = []
        for item in self.parsed.tokens:
            if item.ttype is Keyword and item.value.upper() == 'FROM':
                return list
            elif isinstance(item, Function):
                list.append(self.parse_group(item))
            elif isinstance(item, IdentifierList):
                for ident in item.tokens:
                    if isinstance(ident, Function):
                        list.append(self.parse_group(ident))
        return list

    @staticmethod
    def remove_quotes(input_str):
        """Checks the first and last characters of an input_str
        to see if they are quotation marks [' or "], if so
        the function will strip them and return the string.
        :type input_str: str"""
        #assert isinstance(input_str, str), "Input not of str() type"
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
            return self.filters[comparator](values[0], values[1])

    def generate_like(self, left, comp, right, exist_not):
        if comp.value.upper() == 'LIKE':
            filter = None
            if right.strip().startswith('%') and right.strip().endswith('%'):
                filter = self.filters['%' + comp.value.upper() + '%'](left, right[1:len(right) - 1])
            elif right.strip().startswith('%'):
                filter = self.filters['%' + comp.value.upper()](left, right[1:len(right)])
            elif right.strip().endswith('%'):
                filter = self.filters[comp.value.upper() + '%'](left, right[0:len(right) - 1])
            else:
                filter = self.filters[comp.value.upper()](left, right)

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
                comparison = self.comparisons[item.value.upper()]
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

    def get_where(self):
        """Returns filter object obtained from where of the query in GEE format"""
        val, where = self.parsed.token_next_by(i=sqlparse.sql.Where)
        if where:
            return self.parse_conditions(where.tokens)
        return None

    def apply_group(self, fc, group):
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

    def generate_query(self):
        """Return the GEE object with all filter, groups, functions, etc specified in the query"""
        fc = ee.FeatureCollection(self.table_name)
        filters = self.get_where()
        if filters:
            fc = fc.filter(filters)
        groups = self.get_group_functions()
        if groups:
            for group in groups:
                fc = self.apply_group(fc, group)
        select = self.get_select_list()
        if select and len(select) > 0 and not select[0] == '*':
            fc = fc.select(select)
        self.fc = fc
        return fc

    def execute(self):
        """Execute the GEE object in GEE Server"""
        if self.fc:
            return self.fc.getInfo()
        return None
