import unittest
from sql2gee import SQL2GEE
from ee import apitestcase, Filter, FeatureCollection, Feature


class TestSQL2GEE(apitestcase.ApiTestCase):
    def test_table_name(self):
        sql2gee = SQL2GEE('select pepe from mytable')
        table_name = sql2gee.get_table_name()
        self.assertEqual(table_name, 'mytable')

    def test_fields(self):
        sql2gee = SQL2GEE('select juan from mytable')
        fields = sql2gee.get_select_list()
        self.assertEqual(fields, ['juan'])

    def test_multiple_fields(self):
        sql2gee = SQL2GEE('select pepe, juan from mytable')
        fields = sql2gee.get_select_list()
        self.assertEqual(fields, ['pepe', 'juan'])

    def test_group_select(self):
        sql2gee = SQL2GEE('select count(pepe) from mytable')
        groups = sql2gee.get_group_functions()
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'}])

    def test_several_group_select(self):
        sql2gee = SQL2GEE('select count(pepe), sum(pepe) from mytable')
        groups = sql2gee.get_group_functions()
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'}, {'function': 'SUM', 'value': 'pepe'}])

    def test_several_group_select_several(self):
        sql2gee = SQL2GEE('select count(pepe), sum(pepe), avg(pepe), first(pepe), last(pepe), max(pepe), min(pepe) from mytable')
        groups = sql2gee.get_group_functions()
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'}, {'function': 'SUM', 'value': 'pepe'}, {'function': 'AVG', 'value': 'pepe'}, {'function': 'FIRST', 'value': 'pepe'}, {'function': 'LAST', 'value': 'pepe'}, {'function': 'MAX', 'value': 'pepe'}, {'function': 'MIN', 'value': 'pepe'}])

    def test_none_group_select(self):
        sql2gee = SQL2GEE('select * from mytable')
        groups = sql2gee.get_group_functions()
        self.assertEqual(groups, [])

    def test_where_simple(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2')
        where = sql2gee.get_where()
        correct = Filter().gt('a', 2)
        self.assertEqual(where, correct)

    def test_where_with_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2')
        where = sql2gee.get_where()
        correct = Filter().And(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)

    def test_where_with_or(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 or c = 2')
        where = sql2gee.get_where()
        correct = Filter().Or(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)

    def test_where_with_or_and_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2 or x <= 2')
        where = sql2gee.get_where()
        correct = Filter().Or(Filter().And(Filter().gt('a', 2), Filter().eq('c', 2)), Filter().lte('x', 2))
        self.assertEqual(where, correct)

    def test_where_with_string(self):
        sql2gee = SQL2GEE('select * from mytable where a = "pepe"')
        where = sql2gee.get_where()
        correct = Filter().eq('a', 'pepe')
        self.assertEqual(where, correct)

    def test_generate_query_simple(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" ')
        query = sql2gee.generate_query()
        correct = FeatureCollection('ft:mytable')
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 ')
        query = sql2gee.generate_query()
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2))
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_and_and(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 and b = 2 ')
        query = sql2gee.generate_query()
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('a', 2), Filter().eq('b', 2)))
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_several_conditions(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where (a > 2 or b < 2) and b = 2 ')
        query = sql2gee.generate_query()
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().Or(Filter().gt('a', 2), Filter().lt('b', 2)), Filter().eq('b', 2)))
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2.2 ')

        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_not_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where not a > 2.2 ')

        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2).Not())
        query = sql2gee.generate_query()
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_like_eq(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', '2'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_like_startsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2%" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().stringStartsWith('a', '2'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_like_endsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().stringEndsWith('a', '2'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_like_contains(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_not_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a not like "%2%" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2').Not())
        query = sql2gee.generate_query()
        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_like_and_gt(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" and b > 2 ')

        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().stringContains('a', '2'), Filter().gt('b', 2)))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_gt_and_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where b > 2 and a like "%2%"')

        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('b', 2), Filter().stringContains('a', '2')))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a = "a" ')

        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', "a"))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_in(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1, 2) ')

        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1, 2]))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_in_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1.2, 2) ')

        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1.2, 2]))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_in_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in ("a", "b") ')

        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', ['a', 'b']))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_is(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is NULL ')

        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', 'null'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_generate_query_simple_with_where_is_not(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is not NULL ')

        correct = FeatureCollection('ft:mytable').filter(Filter().neq('a', 'null'))
        query = sql2gee.generate_query()

        self.assertEqual(query, correct)

    def test_fail_generate_query_simple_with_where_is_incorrect(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select * from "ft:mytable" where a is "2" ')

            query = sql2gee.generate_query()

        self.assertTrue('IS only support NULL value' in context.exception)

    def test_fail_table_not_found(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select * from a,b')
            sql2gee.generate_query()
        self.assertTrue('Table not found' in context.exception)

    def test_fail_table_not_found(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select count(*) from a')
            sql2gee.generate_query()
        self.assertTrue('* not allowed' in context.exception)
