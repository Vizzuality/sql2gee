from __future__ import print_function
import pytest
from sql2gee import SQL2GEE
from ee import apitestcase, Filter, FeatureCollection

class TestSQL2GEE(apitestcase.ApiTestCase):

    def test_obtain_class_docstring(self):
        sql = 'select * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
        q = SQL2GEE(sql)
        dstring = q.__doc__
        assert isinstance(dstring, str), "Docstring not returned"
        assert len(dstring) > 0, "Class docstring was empty"
        return

    def test_identify_feature_queries(self):
        err = 'Unable to determine type of request for sql:'
        feature_qlist = [
            'select pepe from mytable',
            'SELECT TOP 1 * FROM mytable ORDER BY unique_column DESC',
            'select * from mytable where a > 2 and c = 2 or x <= 2']
        for query in feature_qlist:
            q = SQL2GEE(query)
            assert q._is_image_request is False, ' '.join([err, q._raw])
            del q
        return

    def test_identify_image_queries(self):
        err = 'Unable to determine type of request for sql:'
        image_qlist = [
            'select ST_METADATA(*) from myimage',
            'select ST_METADATA(band1) from myimage',
            'select ST_METADATA(band1) from myimage',
            'select ST_HISTOGRAM(*) from myimage',
            'select ST_SUMMARYSTATS(*) from myimage']
        for query in image_qlist:
            q = SQL2GEE(query)
            assert q._is_image_request is True, ' '.join([err, q._raw])
            del q
        return

    def test_fields_property(self):
        q = SQL2GEE('select juan from mytable')
        self.assertEqual(q.fields, ['juan'])
        return

    def test_identify_fc_limit(self):
        q = SQL2GEE('select width from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT 3')
        assert q.limit == 3, 'LIMIT not correctly detected'
        return

    def test_halt_at_bad_fc_limit(self):
        q = SQL2GEE('select width from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT -3')
        with pytest.raises(Exception):
            _ = q.limit
        return

    def test_fail_too_many_image_keywords(self):
        """An Error should be returned if multiple image keywords given. This may not be the
        right behaviour, will need to check this after the library is more developed."""
        q = SQL2GEE('select ST_SUMMARYSTATS(*), ST_HISTOGRAM(*) from myimage')
        with pytest.raises(ValueError):
            _ = q._is_image_request
        return

    def test_table_name_property(self):
        sql2gee = SQL2GEE('select pepe from mytable')
        table_name = sql2gee.target_data
        self.assertEqual(table_name, 'mytable')
        sql2gee = SQL2GEE('SELECT TOP 1 * FROM mytable ORDER BY unique_column DESC')
        table_name = sql2gee.target_data
        self.assertEqual(table_name, 'mytable')
        return

    def test_multiple_fields_property(self):
        q = SQL2GEE('select pepe, juan, bob from mytable')
        self.assertEqual(q.fields, ['pepe', 'juan', 'bob'])
        return

    def test_group_select_property(self):
        q = SQL2GEE('select count(pepe) from mytable')
        self.assertEqual(q.group_functions, [{'function': 'COUNT', 'value': 'pepe'}])
        return

    def test_several_group_select_property(self):
        q = SQL2GEE('select count(pepe), sum(pepe) from mytable')
        self.assertEqual(q.group_functions, [{'function': 'COUNT', 'value': 'pepe'},
                                             {'function': 'SUM', 'value': 'pepe'}])
        return

    def test_long_group_select(self):
        sql = 'select count(pepe), sum(pepe), avg(pepe), first(pepe), last(pepe), max(pepe), min(pepe) from mytable'
        q = SQL2GEE(sql)
        self.assertEqual(q.group_functions, [{'function': 'COUNT', 'value': 'pepe'},
                                             {'function': 'SUM', 'value': 'pepe'},
                                             {'function': 'AVG', 'value': 'pepe'},
                                             {'function': 'FIRST', 'value': 'pepe'},
                                             {'function': 'LAST', 'value': 'pepe'},
                                             {'function': 'MAX', 'value': 'pepe'},
                                             {'function': 'MIN', 'value': 'pepe'}])
        return

    def test_empty_group_select(self):
        sql2gee = SQL2GEE('select * from mytable')
        groups = sql2gee.group_functions
        self.assertEqual(groups, [])
        return

    def test_where_simple(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2')
        where = sql2gee.where
        correct = Filter().gt('a', 2)
        self.assertEqual(where, correct)
        return

    def test_where_with_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2')
        where = sql2gee.where
        correct = Filter().And(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)
        return

    def test_where_with_or(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 or c = 2')
        where = sql2gee.where
        correct = Filter().Or(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)

    def test_where_with_or_and_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2 or x <= 2')
        where = sql2gee.where
        correct = Filter().Or(Filter().And(Filter().gt('a', 2), Filter().eq('c', 2)), Filter().lte('x', 2))
        self.assertEqual(where, correct)
        return

    def test_where_with_string(self):
        sql2gee = SQL2GEE('select * from mytable where a = "pepe"')
        where = sql2gee.where
        correct = Filter().eq('a', 'pepe')
        self.assertEqual(where, correct)
        return

    def test_simple_feature_collection(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" ')
        query = sql2gee._feature_collection
        correct = FeatureCollection('ft:mytable')
        self.assertEqual(query, correct)
        return

    def test_simple_feature_collection_with_where(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 ')
        query = sql2gee._feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_and_and(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 and b = 2 ')
        query = sql2gee._feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('a', 2), Filter().eq('b', 2)))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_several_conditions(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where (a > 2 or b < 2) and b = 2 ')
        query = sql2gee._feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().Or(Filter().gt('a', 2), Filter().lt('b', 2)), Filter().eq('b', 2)))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2.2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_not_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where not a > 2.2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2).Not())
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_like_eq(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', '2'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_startsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringStartsWith('a', '2'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_like_endsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringEndsWith('a', '2'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_like_contains(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_not_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a not like "%2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2').Not())
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_like_and_gt(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" and b > 2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().stringContains('a', '2'), Filter().gt('b', 2)))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_gt_and_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where b > 2 and a like "%2%"')
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('b', 2), Filter().stringContains('a', '2')))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a = "a" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', "a"))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_in(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1, 2) ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1, 2]))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_in_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1.2, 2) ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1.2, 2]))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_in_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in ("a", "b") ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', ['a', 'b']))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_is(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is NULL ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', 'null'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_is_not(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is not NULL ')
        correct = FeatureCollection('ft:mytable').filter(Filter().neq('a', 'null'))
        query = sql2gee._feature_collection
        self.assertEqual(query, correct)
        return

    def test_fail_generate_feature_collection_with_where_is_incorrect(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select * from "ft:mytable" where a is "2" ')
            _ = sql2gee._feature_collection
        self.assertTrue('IS only support NULL value' in context.exception)
        return

    # def test_fail_table_not_found(self):
    #     q = SQL2GEE('select * from a, b')
    #     with pytest.raises(Exception):
    #         print("here i am:", q.response)
    #         _ = q.response
    #     return

    def test_fail_table_not_found_extended(self):
        q = SQL2GEE('select count(*) from a')
        with pytest.raises(Exception):
            _ = q.response
        return

    def test_fail_no_table_given(self):
        sql = "SELECT pepe FROM"
        q = SQL2GEE(sql)
        with pytest.raises(Exception):
            _ = q.response
        return

    def test_fail_group_function(self):
        sql = "SELECT MIDDLE() from mytable"
        q = SQL2GEE(sql)
        with pytest.raises(ValueError):
            _ = q.response
        return