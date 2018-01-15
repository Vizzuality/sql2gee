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
    return GeeFactory(self.json_sql, self.geojson, self.flags).response()
