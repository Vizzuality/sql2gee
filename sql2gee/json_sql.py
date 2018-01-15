import requests

class JsonSql(object):
  """docstring for JsonSql"""
  def __init__(self, sql):
    super(JsonSql, self).__init__()
    self.sql = sql

  def to_json(self):
    url = 'https://api.resourcewatch.org/v1/convert/sql2SQL'
    return requests.get(url, params = { 'sql': self.sql }).json()
