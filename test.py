import ee;

from sql2gee import SQL2GEE

ee.Initialize()
from sql2gee.utils.jsonSql import JsonSql
import json

# ee.data.setDeadline(120000)
### For debugging and testing
# import pdb; pdb.set_trace()
# from pympler.tracker  import SummaryTracker
# import cProfile, pstats, io
# tracker = SummaryTracker()
# pr = cProfile.Profile()
# pr.enable()


## Feature Collection 
# sql = "select sum(mean_elev), count(mean_elev) from 'GLIMS/2016' group by glac_name, rec_status order by glac_name limit 20"

## Image Collection 
gstore = "https://api.resourcewatch.org/v1/geostore/89cb48bcd6888a2d4c95df12babff9cc"
# r = requests.get(gstore).json().get('data').get('attributes').get('geojson')
s = json.loads(
    '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-99.66796875,38.87392853923629]}}]}')
# print(r)
# sql = "select sum(area), anlys_time from 'GLIMS/2016'  group by anlys_time order by anlys_time asc limit 10"
# sql = "select first(pr) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 284191200000"

sql = "select first(pr) as x, avg(bi) as y, min(bi) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start >= 1533448800000 and ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[-99.66796875,38.87392853923629]}'),4326), the_geom)"

myQuery = SQL2GEE(JsonSql(sql).to_json())

# print(r)
# myQuery = SQL2GEE(JsonSql(sql).to_json(), geojson=r)

# pdb.run('myQuery.response()')


print(myQuery.response())
# print(myQuery.type)

# pr.disable()
# pr.dump_stats('test_file')
# s = io.StringIO()
# sortby = 'cumulative'
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print(s.getvalue())
# tracker.print_diff()

# -- ASSETS
# -- Image Collections: -- 'COPERNICUS/S2', 'HYCOM/GLBu0_08/sea_temp_salinity', 'IDAHO_EPSCOR/GRIDMET'
# -- F. Collections: --- 'GLIMS/2016', 'USGS/WBD/2017/HUC10','USDOS/LSIB/2013'
# 
# -- Queries I. collection over a geometry or at global scale
# select * from 'IDAHO_EPSCOR/GRIDMET' limit 2
# select status, pr from 'IDAHO_EPSCOR/GRIDMET' limit 10 -- subset of columns/bands
# select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' limit 10
# select status from 'IDAHO_EPSCOR/GRIDMET' where status='permanent' order by system:time_start desc, system:asset_size asc limit 10
# select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 284191200000 order by system:time_start asc limit 10
# select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > '05/01/2018' order by system:time_start asc limit 10
# select avg(B1), GENERATION_TIME, MGRS_TILE from 'COPERNICUS/S2' where CLOUDY_PIXEL_PERCENTAGE < 0.1 group by MGRS_TILE, GENERATION_TIME limit 10
# 
# -- Queries F. collection
# 
# select * from 'GLIMS/2016' limit 10
# select * from 'GLIMS/2016' where rec_status like 'okay' limit 10
# select sum(area) from 'GLIMS/2016' where max_elev > 3000
# select sum(area), anlys_time from 'GLIMS/2016'  group by anlys_time order by anlys_time asc limit 10

# --- Image 'UMD/hansen/global_forest_change_2015'
# SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'
#
