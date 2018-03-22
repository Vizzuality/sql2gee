import numpy as np
import requests
import sys
import pytest
from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql
import ee

#Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    # Else, assume you have an EE_private_key environment variable with authorisation, as on Travis-CI
    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
    ee.Initialize(credentials, 'https://earthengine.googleapis.com')

def test_metadata_icollection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = 'ImageCollection'
    assert q.metadata['type'] == response, "metadata type incorrect"
    return

def test_icollection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 2
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_subsectselect_query():
    sql = "select status, pr from 'IDAHO_EPSCOR/GRIDMET' limit 10"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_where_query():
    sql = "select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' limit 10"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    print(q)
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_orderby_query():
    sql = "select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' order by system:time_start desc, system:asset_size asc limit 10"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_agg_query():
    sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 284191200000 order by system:time_start asc limit 10"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_agg_timeFilter_query():
    sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > '05-01-2018' order by system:time_start asc limit 10"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

def test_icollection_groupby_query():
    gstore = "https://api.resourcewatch.org/v1/geostore/ca38fa80a4ffa9ac6217a7e0bf71e6df"
    r = requests.get(gstore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(water) from 'JRC/GSW1_0/MonthlyHistory' where system:time_start > '05-01-2013' group by month order by system:time_start asc limit 10"
    q = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    response = 10
    assert len(q) == response, "BASIC limit query incorrect"
    return

