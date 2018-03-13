from sql2gee import SQL2GEE
import ee; ee.Initialize()
from utils.jsonSql import JsonSql

### For debugging and testing
#import pdb; pdb.set_trace()
#from pympler.tracker  import SummaryTracker
#import cProfile, pstats, io
#tracker = SummaryTracker()
#pr = cProfile.Profile()
#pr.enable()

#sql=""" 
#SELECT cc, sum(iso_num) AS x, avg(cc) AS xm, min(avg_vis) AS x,'ddd' as d, avg_vis
#FROM 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS'
#WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Polygon\",\"coordinates\":[[[-5.273512601852417,42.81137220349083],[-5.273512601852417,42.811803118457306],[-5.272732079029083,42.811803118457306],[-5.272732079029083,42.81137220349083],[-5.273512601852417,42.81137220349083]]]}'), 4326), the_geom) 
#and iso_num > 2 
#and iso_num < 10 
#or iso_num = 2
#order by y asc
#GROUP BY x 
#order by x asc 
#LIMIT 1 
#"""
## Feature Collection 
#sql = "select sum(mean_elev), count(mean_elev) from 'GLIMS/2016' group by glac_name, rec_status order by glac_name limit 20"

## Image Collection 

sql = "select sum(pr), avg(tmmn) from 'IDAHO_EPSCOR/GRIDMET' where system:time_start > 284191200000 order by system:time_start asc limit 10"


myQuery = SQL2GEE(JsonSql(sql).to_json())

#pdb.run('myQuery.response()')
print(myQuery.response())

#pr.disable()
#pr.dump_stats('test_file')
#s = io.StringIO()
#sortby = 'cumulative'
#ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#ps.print_stats()
#print(s.getvalue())
#tracker.print_diff()






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
# select * from 'GLIMS/2016' where anlys_time limit 10
# select sum(area) from 'GLIMS/2016' where min_elev < 1000
# select sum(area), anlys_time from 'GLIMS/2016'  group by anlys_time order by anlys_time asc limit 10
# 
#--- Image 'UMD/hansen/global_forest_change_2015'
# SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'
#
