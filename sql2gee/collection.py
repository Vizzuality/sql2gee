from feature_collection import FeatureCollection
from image_collection import ImageCollection

class Collection(object):
  """docstring for Collection"""
  def __init__(self, type):
    super(Collection, self).__init__()
    self.type = type
    
  def response():
    if self.type == 'ImageCollection':
      return ImageCollection().response()
    elif self.type == 'FeatureCollection':
      return FeatureCollection().response()