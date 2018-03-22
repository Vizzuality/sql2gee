from requests import get

class JsonSql(object):
  """Takes a string of SQL and converts it to JSON"""
  def __init__(self, sql):
    self.sql = sql

  def to_json(self):
    url = 'https://api.resourcewatch.org/v1/convert/sql2SQL' 
    return get(url, params = { 'sql': self.sql }).json()
