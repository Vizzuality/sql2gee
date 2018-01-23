import sqlparse
from sqlparse.tokens import Keyword
from sqlparse.sql import Identifier, IdentifierList, Function, Parenthesis, Comparison

class Image(object):
  """docstring for Image"""
  def __init__(self, sql, json):
    super(Image, self).__init__()
    self.sql = sql
    self.json = json
    self._parsed = sqlparse.parse(sql)[0]

  @property
  def group_functions(self):
    """Returns the group function with column names specified in the query:
    e.g. from sql input of 'select count(pepe) from mytable', a dictionary of
    {'function': 'COUNT', 'value': 'pepe'} should be returned by self.group_functions"""
    group_list = []

    for t in self._parsed.tokens:
      if t.ttype is Keyword and t.value.upper() == 'FROM':
        return group_list
      elif isinstance(t, Function):
        group_list.append(self.token_to_dictionary(t))
      elif isinstance(t, IdentifierList):
        for identity in t.tokens:
          if isinstance(identity, Function):
            group_list.append(self.token_to_dictionary(identity))

    return group_list

  @staticmethod
  def token_to_dictionary(token_list):
    """ Receives a token e.g.('count(pepe)') and converts it into a dict
    with key:values for function and value ."""
    assert isinstance(token_list, sqlparse.sql.Function), 'unexpected datatype'
    d = {}

    for t in token_list:
      if isinstance(t, Identifier):
        d['function'] = str(t).upper()
      elif isinstance(t, Parenthesis):
        value = t.value.replace('(', '').replace(')', '').strip()
        d['value'] = value

    return d

  def histogram(self):
    """Retrieve ST_HISTOGRAM()-like info. This will return a dictionary object with bands as keys, and for each
    band a nested list of (2xn) for bin and frequency. If the user wants us to use the optimum bin number,
    they can pass n-bins 'auto' instead of an integer.
    """
    tmp_dic = {}

    for function in self.group_functions:
      if function['function'].lower() == "st_histogram":
        values = function['value']
        assert len(values) > 0, "ST_Histogram must be called with arguments"

    hist_args = self.extract_postgis_arguments(values, ['raster','band_id', 'n_bins', 'bool'])
    _, band_of_interest, input_bin_num, dont_flip_order = hist_args
    input_min, input_max, auto_bins = self._default_histogram_inputs(band_of_interest)

    if not input_bin_num:
      input_bin_num = auto_bins

    d = {}
    input_max = input_max + 1  # In EE counting the min -> max range is exc. at max, so need to increment here.
    d['reducer'] = ee.Reducer.fixedHistogram(input_min, input_max, input_bin_num)
    d['bestEffort'] = True

    if self.geojson:
      d['geometry'] = self.geojson

    tmp_response = ee.Image(self.target_data).select(band_of_interest).reduceRegion(**d).getInfo()

    if dont_flip_order:
      tmp_dic[band_of_interest] = tmp_response[band_of_interest]
    else:
      tmp_dic[band_of_interest] = tmp_response[band_of_interest][:][::-1]
      
    return tmp_dic

  def st_metadata(self):
    """The image property Metadata dictionary returned from Earth Engine."""
    metadata=self._metadata['properties'].copy()
    metadata.update({"bands": self._metadata['bands']})
    assert metadata != None, "No metadata available"

    return metadata

    def st_bandmetadata(self):
      """Return only metadata for a specifically requested band, like postgis function"""
      for function in self.group_functions:
        if function['function'].lower() == "st_bandmetadata":
          values = function['value']
          assert len(values) > 0, "raster string and bandnum integer (or band key string) must be provided"
          _, nband = self.extract_postgis_arguments(values, ['raster','band_id'])

      for band in self._metadata.get('bands'):
        if band.get('id') == nband:
          tmp_meta = band

      return tmp_meta

  def st_bandmetadata(self):
    """Return only metadata for a specifically requested band, like postgis function"""
    for function in self.group_functions:
      if function['function'].lower() == "st_bandmetadata":
        values = function['value']
        assert len(values) > 0, "raster string and bandnum integer (or band key string) must be provided"
        _, nband = self.extract_postgis_arguments(values, ['raster','band_id'])

    for band in self._metadata.get('bands'):
      if band.get('id') == nband:
        tmp_meta = band
            
    return tmp_meta

  def summary_stats(self):
    """Return a dictionary object of summary stats like the postgis function ST_SUMMARYSTATS()."""
    d = {}
    for band in self._band_names:
      d[band] = {'count': self._reduce_image[band+'_count'],
                 'sum': self._reduce_image[band+'_sum'],
                 'mean': self._reduce_image[band+'_mean'],
                 'stdev':self._reduce_image[band+'_stdDev'],
                 'min': self._reduce_image[band+'_min'],
                 'max': self._reduce_image[band+'_max']
                 }
    return d

  def st_valuecount(self):
    """Return only metadata for a specifically requested band, like postgis function"""
    #tmp_dic = {}
    for function in self.group_functions:
      if function['function'].lower() == "st_valuecount":
        values = function['value']
        assert len(values) > 0, "raster string and bandnum integer (or band key string) must be provided"
        _, band_of_interest, no_drop_no_data_val = self.extract_postgis_arguments(values, ['raster','band_id', 'bool'])

    d = {}
    d['reducer'] = ee.Reducer.frequencyHistogram().unweighted()
    d['bestEffort'] = True
    d['maxPixels'] =  9000000000

    if self.geojson:
      d['geometry'] = self.geojson

    tmp_response = ee.Image(self.target_data).select(band_of_interest).reduceRegion(**d).getInfo()

    if no_drop_no_data_val != True:
      try:
        del tmp_response[band_of_interest]['null']
      except KeyError:
        pass
    #else:    
        #tmp_dic[band_of_interest] = tmp_response[band_of_interest]

    return tmp_response

  def extract_postgis_arguments(self, argument_string, list_of_expected):
    """Expects a string list of arguments passed to postgis function, and an ordered list of keys needed
    In this way, we should be able to handle any postgis argument arrangements:
    value_string, ordered keyword list: ['raster', 'band_id', 'n_bins'])
    """
    assert len(argument_string) > 0, "No arguments passed to postgis function"
    value_list = argument_string.split(',')
    assert len(value_list) == len(list_of_expected), "argument string from postgis not equal to list of expected keys"
    return_values = []

    for expected, argument in zip(list_of_expected, value_list):
      if expected is 'raster':
        return_values.append(str(argument.strip()))

      if expected is 'band_id':
        if str(argument.strip().strip("'")) in  self._band_names:
          nband = str(argument.strip().strip("'"))                        
        else:
          numband = int(argument.strip()) - 1  # a zero index for self._band_list
          nband = self._band_names[numband]
              
        assert nband in self._band_names, '{0} is not a valid band name in the requested data.'.format(nband)
        return_values.append(nband)

      if expected is 'n_bins':
        try:
          bins = int(argument.strip())
          assert bins > 0, "Bin number for ST_HISTOGRAM() must be > 0: bins = {0} passed.".format(bins)
        except:
          assert argument.strip().lower() == 'auto',"Either pass int number of desired bins, or auto"
          bins = None
          
        return_values.append(bins)

      if expected is 'bool':
        bool_arg = None
        if argument.strip().lower() == 'true': bool_arg = True
        if argument.strip().lower() == 'false': bool_arg = False
        assert isinstance(bool_arg, bool), "Boolean not correctly set"
        return_values.append(bool_arg)

    assert len(return_values) == len(list_of_expected),'Failed to identify all keywords :('
    return return_values

  def _default_histogram_inputs(self, band_name):
    """Return the optimum histogram min, max, bins, using Freedman-Diaconis method, to be used by default
    band_name is the dictionary key (that relates to self._band_names)
    """
    band_max = self._reduce_image[band_name +'_max']
    band_count = self._reduce_image[band_name +'_count']
    band_min = self._reduce_image[band_name +'_min']
    band_iqr = self._band_IQR[band_name]
    band_n = self._reduce_image[band_name +'_count']
    bin_width = (2 * band_iqr * (band_n ** (-1/3)))
    
    try:
      num_bins = int((band_max - band_min) / bin_width)
    except ZeroDivisionError:
      num_bins = band_count ** 0.5  # as a last-resort, use the square root of the counts to set-bin size
    return band_min, band_max, num_bins

  def _metadata(self):
    """Property that holds the Metadata dictionary returned from Earth Engine."""
    if self._is_image_request:
      return ee.Image(self.target_data).getInfo()
    
  def response(self):
    for func in self.group_functions:
      if func["function"].lower() == 'st_histogram':
        return self.histogram
      if func["function"].lower() == 'st_metadata':
        return self.st_metadata
      if func["function"].lower() == 'st_bandmetadata':
        return self.st_bandmetadata
      if func["function"].lower() == 'st_summarystats':
        return self.summary_stats
      if func["function"].lower() == 'st_valuecount':
        return self.st_valuecount
    # except ee.EEException:
    #   # If we hit the image composite bug then add a global region to group the image together and try again
    #   return SQL2GEE(sql=self._raw, geojson=_default_geojson)._image