import numpy as np
import requests
import sys
import pytest
from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql
import ee

# Quick hack, if using a local mac, assume you can initilise using the below...
#if sys.platform == 'darwin':
#    ee.Initialize()
#else:
#    # Else, assume you have an EE_private_key environment variable with authorisation, as on Travis-CI
#    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
#    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
#    ee.Initialize(credentials, 'https://earthengine.googleapis.com')
#
#def test_metadata_table_query():
#    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    response = {'type': 'FeatureCollection', 'columns': {'date': 'Number', 'height': 'Number', 'lng': 'Number', 'title': 'String', 'url': 'String', 'user_id': 'Number', 'user_name': 'String', 'width': 'Number'}, 'id': 'ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo', 'version': '', 'properties': {'name': 'SF Panoramio Photos +ID', 'DocID': '1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo'}}
#    assert q.metadata == response, "BASIC COUNT query incorrect"
#    return
#
#def test_select_table_query():
#    sql = 'select * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" limit 1'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    response = {'type': 'FeatureCollection', 'columns': {'date': 'Number', 'height': 'Number', 'lng': 'Number', 'title': 'String', 'url': 'String', 'user_id': 'Number', 'user_name': 'String', 'width': 'Number'}, 'id': 'ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo', 'version': '', 'properties': {'name': 'SF Panoramio Photos +ID', 'DocID': '1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo'}}
#    assert q.metadata == response, "BASIC COUNT query incorrect"
#    return
#
#def test_count_table_query():
#    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['count'] == [1919], "BASIC COUNT query incorrect"
#    return
#
#def test_count_table_query_with_where_statement():
#    sql = 'select count(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 400'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['count'] == [1677], "COUNT with WHERE query incorrect"
#    return
#
#def test_max_table_query():
#    sql = 'select MAX(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" limit 2'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    print( q.response()[0])
#    assert q.response()[0]['max'] == [500.0], "Basic MAX query incorrect"
#    return
#
#def test_min_table_query():
#    sql = 'select MIN(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['min'] == [125.0], "Basic MIN query incorrect"
#    return
#
#def test_sum_table_query():
#    sql = 'select SUM(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['sum'] == [924091.0], "Basic SUM query incorrect"
#    return
#
#def test_sum_with_where_table_query():
#    sql = 'select SUM(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 400'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['sum'] == [83306.0], "SUM with WHERE query incorrect"
#    return
#
#def test_avg_with_where_table_query():
#    sql = 'select AVG(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 400'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    print(q.response()[0])
#    assert q.response()[0]['mean'] == [354.4936170212766], "AVG with WHERE query incorrect"
#    return
#
#def test_avg_with_doublewhere_table_query():
#    sql = 'select AVG(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width > 100 and width < 280'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['mean'] == [212.25], "Complex AVG (with compound WHERE) query incorrect"
#    return
#
#def test_first_table_query():
#    sql = 'select FIRST(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    print(q.response())
#    assert q.response()[0]['first'] == [500.0], "Simple FIRST query incorrect"
#    return
#
#def test_first_with_where_table_query():
#    sql = 'select FIRST(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width < 200 order by width desc'
#    q = SQL2GEE(JsonSql(sql).to_json())
#    assert q.response()[0]['first'] == [125.0], "FIRST with WHERE query incorrect"
#    return
#
## This functions aren't suported by sql2json microservice
##def test_var_table_query():
##    sql = 'select VAR(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
##    q = SQL2GEE(JsonSql(sql).to_json())
##    assert q.response()[0]['var'] == [2423.5074511457533], "Simple VAR query incorrect"
#
##def test_var_table_where_all_equal():
##    sql = 'select VAR(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE width = 500'
##    q = SQL2GEE(JsonSql(sql).to_json())
##    assert q.response()[0]['var'] == [0.0], "Simple VAR query incorrect"
#
##def test_stdev_table():
##    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
##    q = SQL2GEE(JsonSql(sql).to_json())
##    assert q.response()[0]['stdev'] == [49.22913213886421], "Simple STDEV query incorrect"
#
##def test_stdev_width_lt_table():
##    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width < 500'
##    q = SQL2GEE(JsonSql(sql).to_json())
##    assert q.response()[0]['stdev'] == [35.01078172011275], "STDEV with WHERE LT 500 query incorrect"
#
##def test_stdev_width_eq_table():
##    sql = 'select STDEV(width) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" where width = 500'
##    q = SQL2GEE(JsonSql(sql).to_json())
##    assert q.response()[0]['stdev'] == 0.0, "STDEV with WHERE EQ 500 query incorrect"
