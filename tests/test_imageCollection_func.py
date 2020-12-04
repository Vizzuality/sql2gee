import os
import sys

import ee
import requests
#from datatest import validate, accepted

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


def test_metadata_image_collection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = q.response()
    assert response == [{'status': 'permanent', 'system:asset_size': 27580337, 'system:footprint': {
        'coordinates': [[-124.83354858089547, 25.003807946517743], [-122.08046873314143, 24.995926537448984],
                        [-116.66640625473028, 24.963260502976674], [-110.35000001111823, 24.98231582244473],
                        [-104.93593745133236, 24.982315818720387], [-100.42421873312358, 24.995926491821308],
                        [-95.91249996019583, 24.982315874124307], [-90.49843745062729, 24.982315828547943],
                        [-85.98671867951936, 24.995926496850476], [-80.57265622055839, 24.963260508093065],
                        [-74.25624993114793, 24.982315802057173], [-66.9914877989776, 24.937365013255352],
                        [-66.97329042095092, 49.4620585688528], [-74.25625003685488, 49.462575843249724],
                        [-83.27968745024836, 49.46257586252526], [-90.49843747394075, 49.462575896553865],
                        [-103.1312499346856, 49.46257587117741], [-113.9593748919571, 49.46257584884527],
                        [-124.85170940475892, 49.4620585601637], [-124.83354858089547, 25.003807946517743]],
        'type': 'LinearRing'}, 'system:index': '19790101', 'system:time_end': 284083200000,
                         'system:time_start': 284018400000}, {'status': 'permanent', 'system:asset_size': 27598811,
                                                              'system:footprint': {'coordinates': [
                                                                  [-124.83354858089547, 25.003807946517743],
                                                                  [-122.08046873314143, 24.995926537448984],
                                                                  [-116.66640625473028, 24.963260502976674],
                                                                  [-110.35000001111823, 24.98231582244473],
                                                                  [-104.93593745133236, 24.982315818720387],
                                                                  [-100.42421873312358, 24.995926491821308],
                                                                  [-95.91249996019583, 24.982315874124307],
                                                                  [-90.49843745062729, 24.982315828547943],
                                                                  [-85.98671867951936, 24.995926496850476],
                                                                  [-80.57265622055839, 24.963260508093065],
                                                                  [-74.25624993114793, 24.982315802057173],
                                                                  [-66.9914877989776, 24.937365013255352],
                                                                  [-66.97329042095092, 49.4620585688528],
                                                                  [-74.25625003685488, 49.462575843249724],
                                                                  [-83.27968745024836, 49.46257586252526],
                                                                  [-90.49843747394075, 49.462575896553865],
                                                                  [-103.1312499346856, 49.46257587117741],
                                                                  [-113.9593748919571, 49.46257584884527],
                                                                  [-124.85170940475892, 49.4620585601637],
                                                                  [-124.83354858089547, 25.003807946517743]],
                                                                  'type': 'LinearRing'},
                                                              'system:index': '19790102',
                                                              'system:time_end': 284169600000,
                                                              'system:time_start': 284104800000}]
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


def test_image_collection_simple_agg_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 1522548800000 "
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert "pr_sum" in response[0].keys()
    assert len(response[0].keys()) == 1
    return


def test_image_collection_2_agg_geostore_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 1522548800000"
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert "pr_sum_sum" in response[0].keys()
    assert "tmmn_mean_mean" in response[0].keys()
    assert len(response[0].keys()) == 2
    return


def test_image_collection_3_agg_geostore_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr), avg(tmmn) , min(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 1522548800000"
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert "pr_sum_sum" in response[0].keys()
    assert "tmmn_mean_mean" in response[0].keys()
    assert "tmmn_min_min" in response[0].keys()
    assert len(response[0].keys()) == 3
    return


def test_image_collection_4_agg_geostore_query():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select sum(pr), avg(tmmn) , min(tmmn), max(tmmx) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 1522548800000"
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert "pr_sum_sum" in response[0].keys()
    assert "tmmn_mean_mean" in response[0].keys()
    assert "tmmx_max_max" in response[0].keys()
    assert len(response[0].keys()) == 4
    return


# TODO: make test more specific
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


def test_image_collection_with_greater_where_clause():
    sql = "select * from 'NCEP_RE/sea_level_pressure' where system:time_start > 1522548800000 limit 5"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert response == [{'system:asset_size': 14821,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_2018040106',
                         'system:time_end': 1522562400000,
                         'system:time_start': 1522562400000},
                        {'system:asset_size': 14740,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_2018040112',
                         'system:time_end': 1522584000000,
                         'system:time_start': 1522584000000},
                        {'system:asset_size': 14818,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_2018040118',
                         'system:time_end': 1522605600000,
                         'system:time_start': 1522605600000},
                        {'system:asset_size': 14715,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_2018040200',
                         'system:time_end': 1522627200000,
                         'system:time_start': 1522627200000},
                        {'system:asset_size': 14769,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_2018040206',
                         'system:time_end': 1522648800000,
                         'system:time_start': 1522648800000}]
    return


def test_image_collection_with_geometry_where_clause():
    sql = "select * from 'NCEP_RE/sea_level_pressure' where ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[-110.22939224192194,19.986126139624318]}'),4326),the_geom) limit 5"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 5
    assert response == [{'system:asset_size': 12575,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_1948010100',
                         'system:time_end': -694310400000,
                         'system:time_start': -694310400000},
                        {'system:asset_size': 12815,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_1948010106',
                         'system:time_end': -694288800000,
                         'system:time_start': -694288800000},
                        {'system:asset_size': 13149,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_1948010112',
                         'system:time_end': -694267200000,
                         'system:time_start': -694267200000},
                        {'system:asset_size': 13324,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_1948010118',
                         'system:time_end': -694245600000,
                         'system:time_start': -694245600000},
                        {'system:asset_size': 13417,
                         'system:footprint': {'coordinates': [[-180, -90],
                                                              [180, -90],
                                                              [180, 90],
                                                              [-180, 90],
                                                              [-180, -90]],
                                              'type': 'LinearRing'},
                         'system:index': 'slp_1948010200',
                         'system:time_end': -694224000000,
                         'system:time_start': -694224000000}]
    return


def test_image_collection_group_by_with_geometry_where_clause():
    sql = "select first(slp) as calculated_slp, system:asset_size from 'NCEP_RE/sea_level_pressure' where ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[-110.22939224192194,19.986126139624318]}'),4326),the_geom) group by system:asset_size limit 5"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 5
    assert "calculated_slp" in response[0].keys()
    assert "system:asset_size" in response[0].keys()
    assert "system:asset_size" in response[0].keys()
    assert response == [{'calculated_slp': 9.223372036854776e+18, 'system:asset_size': 34},
                        {'calculated_slp': 101500, 'system:asset_size': 12575},
                        {'calculated_slp': 101400, 'system:asset_size': 12815},
                        {'calculated_slp': 101580, 'system:asset_size': 13149},
                        {'calculated_slp': 101150, 'system:asset_size': 13324}]
    return


def test_image_collection_group_by_with_geometry_where_clause_and_multiple_aliases_for_min_and_avg():
    geostore = "https://api.resourcewatch.org/v1/geostore/46e0617e8d2000bd3c36e9e92bb5a35b"
    r = requests.get(geostore).json().get('data').get('attributes').get('geojson')
    sql = "select min(slp) as min_slp, avg(slp) as average_slp from 'NCEP_RE/sea_level_pressure'  group by system:index limit 5"
    response = SQL2GEE(JsonSql(sql).to_json(), geojson=r).response()
    assert len(response) == 5
    assert len(response[0].keys()) == 2
    assert "min_slp" in response[0].keys()
    assert "average_slp" in response[0].keys()
    return


def test_image_collection_group_by_with_geometry_where_clause_and_multiple_aliases_for_first_and_avg():
    sql = "select first(slp) as first_slp, avg(slp) as average_slp from 'NCEP_RE/sea_level_pressure' where ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[-110.22939224192194,19.986126139624318]}'),4326),the_geom) group by system:index limit 5"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 5
    assert len(response[0].keys()) == 2
    assert "first_slp" in response[0].keys()
    assert "average_slp" in response[0].keys()
    return

def test_image_collection_group_by_without_where_clause_and_multiple_aliases():
    sql = "select max(tmmx), avg(tmmx) as average_tmmx from 'IDAHO_EPSCOR/TERRACLIMATE' group by system:index limit 5"
    response = SQL2GEE(JsonSql(sql).to_json()).response()
    assert len(response) == 5
    assert "tmmx_max" in response[0].keys()
    assert "average_tmmx" in response[0].keys()
    return

# TODO: currently failing with "Image.reduceRegion: Provide 'geometry' parameter when aggregating over an unbounded image"
# Need to look into it in the future
# def test_image_collection_group_by_without_where_clause_and_multiple_aliases():
#     sql = "select first(slp) as first_slp, avg(slp) as average_slp from 'NCEP_RE/sea_level_pressure' group by system:index limit 5"
#     response = SQL2GEE(JsonSql(sql).to_json()).response()
#     assert len(response) == 5
#     assert "first_slp" in response[0].keys()
#     assert "average_slp" in response[0].keys()
#     assert response == [{'average_slp': 101500, 'first_slp': 101500, 'system:asset_size': 12575, 'system:footprint': {
#         'coordinates': [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]], 'type': 'LinearRing'},
#                          'system:time_start': -694310400000},
#                         {'average_slp': 101400, 'first_slp': 101400, 'system:asset_size': 12815, 'system:footprint': {
#                             'coordinates': [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]],
#                             'type': 'LinearRing'}, 'system:time_start': -694288800000},
#                         {'average_slp': 101580, 'first_slp': 101580, 'system:asset_size': 13149, 'system:footprint': {
#                             'coordinates': [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]],
#                             'type': 'LinearRing'}, 'system:time_start': -694267200000},
#                         {'average_slp': 101150, 'first_slp': 101150, 'system:asset_size': 13324, 'system:footprint': {
#                             'coordinates': [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]],
#                             'type': 'LinearRing'}, 'system:time_start': -694245600000},
#                         {'average_slp': 101370, 'first_slp': 101370, 'system:asset_size': 13417, 'system:footprint': {
#                             'coordinates': [[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]],
#                             'type': 'LinearRing'}, 'system:time_start': -694224000000}]
#     return
