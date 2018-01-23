from json_sql import JsonSql
from gee_factory import GeeFactory

class SQL2GEE(object):
  """docstring for SQL2GEE"""
  def __init__(self, sql, geojson=None, flags=None):
    super(SQL2GEE, self).__init__()
    self.sql = sql
    self.json_sql = JsonSql(sql).to_json()
    self.geojson = geojson
    self.flags = flags  # <-- Will be used in a later version of the code

  def response(self):
    return GeeFactory(self.sql, self.json_sql, self.geojson, self.flags).response()


#############################

# sql="""
# SELECT cc, sum(iso_num) AS x, avg(cc) AS xm, min(avg_vis) AS x,'ddd' as d, avg_vis
# FROM 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182012'
# WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Polygon\",\"coordinates\":[[[-5.273512601852417,42.81137220349083],[-5.273512601852417,42.811803118457306],[-5.272732079029083,42.811803118457306],[-5.272732079029083,42.81137220349083],[-5.273512601852417,42.81137220349083]]]}'), 4326), the_geom) 
# and iso_num > 2 
# and iso_num < 10 
# or iso_num = 2
# order by y asc
# GROUP BY x 
# LIMIT 1
# """

sql = "SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'"

json = JsonSql(sql).to_json()

print(
  SQL2GEE(sql).response()
)

# print(
#   GeeFactory(json).response()
# )


