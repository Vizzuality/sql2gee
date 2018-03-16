import ee
from cached_property import cached_property

 
class Image(object):
  """docstring for Image"""
  def __init__(self, sql, json, select, filters, _asset_id, geometry=None):
    self.json = json
    self.select = select
    self.group_functions= select[ '_functions']['bands']
    self.geometry = geometry
    self._asset_id = _asset_id
    self._asset = self._asset()

  def _asset(self):
    return ee.Image(self._asset_id)

  @property
  def _reduce_image(self):
      """ Construct a combined reducer dictionary and pass it to a ReduceRegion().getInfo() command.
      If a geometry has been passed to SQL2GEE, it will be passed to ensure only a subset of the band is examined.
      """
      d={}
      d['bestEffort'] = True
      if self.geometry:
          d['geometry'] = self.geometry
      d['reducer'] = ee.Reducer.count().combine(ee.Reducer.sum(), outputPrefix='', sharedInputs=True
                      ).combine(ee.Reducer.mean(), outputPrefix='', sharedInputs=True).combine(
                      ee.Reducer.sampleStdDev(), outputPrefix='', sharedInputs=True).combine(ee.Reducer.min(),
                      outputPrefix='', sharedInputs=True).combine(ee.Reducer.max(), outputPrefix='',
                      sharedInputs=True).combine(ee.Reducer.percentile([25, 75]), outputPrefix='', sharedInputs=True)
      
      return self._asset.select(self.select['_bands']).reduceRegion(**d).getInfo()

  @cached_property
  def _band_IQR(self):
    """Return a dictionary object with the InterQuartileRange (Q3 - Q1) per band."""
    iqr = {}
    for band in self.select['_bands']:
        tmp = self._reduce_image[band + '_p75'] - self._reduce_image[band + '_p25']
        iqr[band] = tmp
        del tmp
    return iqr

  @cached_property
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

    if self.geometry:
      d['geometry'] = self.geometry

    tmp_response = ee.Image(self.target_data).select(band_of_interest).reduceRegion(**d).getInfo()

    if dont_flip_order:
      tmp_dic[band_of_interest] = tmp_response[band_of_interest]
    else:
      tmp_dic[band_of_interest] = tmp_response[band_of_interest][:][::-1]
      
    return tmp_dic

  @property
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

  @cached_property
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

  @cached_property
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

    if self.geometry:
      d['geometry'] = self.geometry

    tmp_response = ee.Image(self.target_data).select(band_of_interest).reduceRegion(**d).getInfo()

    if no_drop_no_data_val != True:
      try:
        del tmp_response[band_of_interest]['null']
      except KeyError:
        pass
    #else:    
        #tmp_dic[band_of_interest] = tmp_response[band_of_interest]

    return tmp_response

  def extract_postgis_arguments(self, argument, list_of_expected):
    """Expects a string list of arguments passed to postgis function, and an ordered list of keys needed
    In this way, we should be able to handle any postgis argument arrangements:
    value_string, ordered keyword list: ['raster', 'band_id', 'n_bins'])
    """
    assert len(argument) > 0, "No arguments passed to postgis function"
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
    
  def response(self):
    print(self.group_functions)
    for func in self.group_functions:
      if func["value"].lower() == 'st_histogram':
        return self.histogram
      if func["value"].lower() == 'st_metadata':
        return self.st_metadata
      if func["value"].lower() == 'st_bandmetadata':
        return self.st_bandmetadata
      if func["value"].lower() == 'st_summarystats':
        return self.summary_stats
      if func["value"].lower() == 'st_valuecount':
        return self.st_valuecount
