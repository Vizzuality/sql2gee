import sys
import ee
import os

from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql

# Quick hack, if using a local mac, assume you can initialise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    EE_ACCOUNT = os.environ['EE_ACCOUNT']
    EE_PRIVATE_KEY_FILE = 'privatekey.json'

    gee_credentials = ee.ServiceAccountCredentials(EE_ACCOUNT, EE_PRIVATE_KEY_FILE)
    ee.Initialize(gee_credentials)

ee.data.setDeadline(200000)


def test_metadata_table_query():
    sql = 'select count(width) from "TIGER/2018/States"'
    sql_gee = SQL2GEE(JsonSql(sql).to_json())
    expected_metadata = {'type': 'TABLE', 'name': 'projects/earthengine-public/assets/TIGER/2018/States',
                         'id': 'TIGER/2018/States', 'updateTime': '2019-06-17T17:48:10.661679Z', 'sizeBytes': '3543775'}
    assert sql_gee.metadata == expected_metadata, "Response metadata incorrect"
    return


def test_limit_table_query():
    sql = 'select * from "TIGER/2018/States" limit 1'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 1, "BASIC COUNT query incorrect"
    return


def test_count_table_query():
    sql = 'select count(NAME) from "TIGER/2018/States"'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['count'] == [56], "BASIC COUNT query incorrect"
    return


def test_count_table_query_with_where_statement():
    sql = 'select count(ALAND) from "TIGER/2018/States" where ALAND > 400000000'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['count'] == [53], "COUNT with WHERE query incorrect"
    return


def test_max_table_query():
    sql = 'select MAX(ALAND) from "TIGER/2018/States" limit 2'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['max'] == [1478839695958], "Basic MAX query incorrect"
    return


def test_min_table_query():
    sql = 'select MIN(ALAND) from "TIGER/2018/States"'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['min'] == [158340391], "Basic MIN query incorrect"
    return


def test_sum_table_query():
    sql = 'select SUM(ALAND) from "TIGER/2018/States"'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['sum'] == [9159859051207], "Basic SUM query incorrect"
    return


def test_sum_with_where_table_query():
    sql = 'select SUM(ALAND) from "TIGER/2018/States" WHERE ALAND > 400000000'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['sum'] == [9159154929857], "SUM with WHERE query incorrect"
    return


def test_avg_with_where_table_query():
    sql = 'select AVG(ALAND) from "TIGER/2018/States" WHERE ALAND > 400000000'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['mean'] == [172814243959.56604], "AVG with WHERE query incorrect"
    return


def test_var_table_query():
    sql = 'select VAR(ALAND) from "TIGER/2018/States"'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['variance'] == [4.640943337611609e+22], "Simple VAR query incorrect"


def test_var_table_where_all_equal():
    sql = 'select VAR(ALAND) from "TIGER/2018/States" WHERE ALAND > 400000000'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['variance'] == [4.744082688545956e+22], "Simple VAR query incorrect"


def test_stdev_table():
    sql = 'select STDEV(ALAND) from "TIGER/2018/States"'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['stdDev'] == [215428487847.16492], "Simple STDEV query incorrect"


def test_stdev_width_lt_table():
    sql = 'select STDEV(ALAND) from "TIGER/2018/States" where ALAND < 400000000'
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response[0]['stdDev'] == [81725709.28450204], "STDEV with WHERE LT 400000000 query incorrect"


def test_limit_on_tables():
    """Test ability to limit the size of SQL table requests"""
    sql = 'select ALAND from "TIGER/2018/States" LIMIT '
    err = 'Response was not equal to size of LIMIT'
    limit = 1
    response = SQL2GEE(JsonSql(sql + str(limit)).to_json()).response()
    assert len(response) == limit, err
    limit = 2
    response = SQL2GEE(JsonSql(sql + str(limit)).to_json()).response()
    assert len(response) == limit, err
    limit = 5
    response = SQL2GEE(JsonSql(sql + str(limit)).to_json()).response()
    assert len(response) == limit, err
    return
