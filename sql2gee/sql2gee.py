from gee_factory import GeeFactory
from cached_property import cached_property

class SQL2GEE(object):
  """docstring for SQL2GEE"""
  def __init__(self, sql, geojson=None, flags=None):
    super(SQL2GEE, self).__init__()
    self.sql = sql
    self.geojson = geojson
    self.flags = flags  # <-- Will be used in a later version of the code
    self.factory = GeeFactory(self.sql, self.geojson, self.flags)
    self._asset_id = self.factory._asset_id
    self.type = self.factory.type
    self.metadata = self.factory.metadata()

  @cached_property
  def response(self):
  	return self.factory.response()


############################# for testing:

sql="""
SELECT cc, sum(iso_num) AS x, avg(cc) AS xm, min(avg_vis) AS x,'ddd' as d, avg_vis
FROM 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS'
WHERE ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Polygon\",\"coordinates\":[[[-5.273512601852417,42.81137220349083],[-5.273512601852417,42.811803118457306],[-5.272732079029083,42.811803118457306],[-5.272732079029083,42.81137220349083],[-5.273512601852417,42.81137220349083]]]}'), 4326), the_geom) 
and iso_num > 2 
and iso_num < 10 
or iso_num = 2
order by y asc
GROUP BY x 
order by x asc
LIMIT 1
"""

#sql = "SELECT ST_HISTOGRAM(raster, lossyear, 15, true) FROM 'UMD/hansen/global_forest_change_2015'"

myQuery = SQL2GEE(sql)

#print( myQuery.type)
print(myQuery.response())


