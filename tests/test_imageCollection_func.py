import sys
import ee
import requests
import os

from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql

# Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    EE_ACCOUNT = os.environ['EE_ACCOUNT']
    EE_PRIVATE_KEY_FILE = 'privatekey.json'

    gee_credentials = ee.ServiceAccountCredentials(EE_ACCOUNT, EE_PRIVATE_KEY_FILE)
    ee.Initialize(gee_credentials)

ee.data.setDeadline(200000)


def test_metadata_image_collection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert q.metadata['type'] == 'IMAGE_COLLECTION', "metadata type incorrect"
    assert len(response) == 2, "BASIC limit query incorrect"
    return


def test_image_collection_where_query():
    sql = "select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' limit 10"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 10, "BASIC limit query incorrect"
    return


def test_image_collection_order_by_query():
    sql = "select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' order by system:time_start desc, system:asset_size asc limit 10"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 10, "BASIC limit query incorrect"
    return


def test_image_collection_agg_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 1522548800000 "
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert len(response) == 1, "BASIC limit query incorrect"
    return


def test_image_collection_agg_timeFilter_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > '05-01-2017' order by system:time_start asc limit 10"
    q = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    response = 1
    assert len(q) == response, "BASIC limit query incorrect"
    return


def test_image_collection_group_by_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(water) from 'JRC/GSW1_2/MonthlyHistory' where system:time_start > '05-01-2013' group by month order by system:time_start asc limit 10"
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert len(response) == 10, "BASIC limit query incorrect"
    return

def test_image_collection_group_by_with_geometry_where_condition():
    sql = "select system:index, first(q25) as q25,first(q50) as q50, first(q75) as q75, mean(q75) as q75_mean from 'projects/resource-watch-gee/cli_051_nexgddp_annual_tasmin' where ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[-110.22939224192194,19.986126139624318]}'),4326),the_geom) group by system:index"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) > 0, f"Empty response: {response}"
    return
