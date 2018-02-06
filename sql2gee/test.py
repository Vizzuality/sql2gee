from sql2gee import SQL2GEE
from json_sql import JsonSql
import pdb; pdb.set_trace()

#sqlc=""" 
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

sql = "SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'"

myQuery = SQL2GEE(JsonSql(sql).to_json())


pdb.run('myQuery.response()')
print(myQuery.response())

