from gee_factory import GeeFactory

class SQL2GEE(object):
  """docstring for SQL2GEE"""
  def __init__(self, sqlscheme, geojson=None, flags=None):
    self.flags = flags  # <-- Will be used in a later version of the code
    self.factory = GeeFactory(sqlscheme, geojson, flags)
    self._asset_id = self.factory._asset_id
    self.type = self.factory.type
    self.metadata = self.factory.metadata()
  
  def response(self):
  	return self.factory.response()


