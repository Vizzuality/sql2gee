Tutorial
========

This is intended as a quick-start guide to using the sql2gee library.

Loading and Authenticating
--------------------------

To use this library you must be able to make Earth Engine requests. To do this, you must be able to authenticate your
session with Google. To set this up, follow `Google's guide <https://developers.google.com/earth-engine/python_install>`_.

Assuming that you are running Python 2.7, have installed sql2gee, and are able to authenticate a session with Earth Engine,
the following examples should work.

First, load sql2gee and the Earth Engine libraries.

.. code-block:: python
   :linenos:

    >>>import ee
    >>>from sql2gee import SQL2GEE
    >>>ee.Initialize()


Simple Queries to Fusion Table data
-----------------------------------

After loading the libraries, you may create SQL queries against either Features (vector data) or rasters (image data).
For example, we may use a public Fusion Table dataset by passing it's ID as a table argument
(e.g. `Panoramic Photos and locations from San Francisco <https://fusiontables.google.com/data?docid=1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo#rows:id=1>`_).

Using the LIMIT keyword
^^^^^^^^^^^^^^^^^^^^^^^

We may obtain the first entry in the Fusion table using the LIMIT keyword.

.. code-block:: python
   :linenos:

    >>>sql = 'select * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT 1'
    >>>q = SQL2GEE(sql)
    >>>q.response
    {u'columns': {u'date': u'Number',
                  u'height': u'Number',
                  u'lng': u'Number',
                  u'title': u'String',
                  u'url': u'String',
                  u'user_id': u'Number',
                  u'user_name': u'String',
                  u'width': u'Number'},
     u'features': [{u'geometry': {u'coordinates': [-122.199705, 37.808411],
                                  u'geodesic': True,
                                  u'type': u'Point'},
                    u'id': u'2',
                    u'properties': {u'date': 1169596800000,
                                    u'height': 375.0,
                                    u'lng': -122.199705,
                                    u'title': u'Oakland California LDS Temple',
                                    u'url': u'http://mw2.google.com/mw-panoramio/photos/medium/551255.jpg',
                                    u'user_id': 99249.0,
                                    u'user_name': u'shaunikadearman',
                                    u'width': 500.0},
                    u'type': u'Feature'}],
     u'properties': {u'DocID': u'1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo',
                     u'name': u'SF Panoramio Photos +ID'},
     u'type': u'FeatureCollection'}

Note that the actual response to our query is returned via the ``response`` property, and it is possible to both
instantiate a class instance and call this property in a single argument, e.g. ``SQL@GEE('select * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" LIMIT 1').response``.


Using the FIRST() aggregator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These data have a column called **lng**, each row of 'which contains a value for Longitude where a photo was taken.

We may request the first value from the **lng** column from the table as follows.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT FIRST(lng) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    >>>q = SQL2GEE(sql)
    >>>q.response
    -122.199705

Counting rows in a table
^^^^^^^^^^^^^^^^^^^^^^^^

We may count the number of rows of **lng** data in the table with the COUNT() aggregator function as follows.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT COUNT(lng) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    >>>q = SQL2GEE(sql)
    >>>q.response
    1919

Restricting Queries from Fusion Table data
------------------------------------------

Simple WHERE Statements
^^^^^^^^^^^^^^^^^^^^^^^

Increasing the complexity, we can ask to return all columns of data from our Fusion Table, where the row matches a specific column value,
in our case, we will use the example of returning data where the **user_name** is equal to **Adnew**.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT * from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE user_name =Adnew'
    >>>q = SQL2GEE(sql)
    >>>q.response
    {u'columns': {u'date': u'Number',
                  u'height': u'Number',
                  u'lng': u'Number',
                  u'title': u'String',
                  u'url': u'String',
                  u'user_id': u'Number',
                  u'user_name': u'String',
                  u'width': u'Number'},
     u'features': [{u'geometry': {u'coordinates': [-122.478504, 37.825853],
                                  u'geodesic': True,
                                  u'type': u'Point'},
                    u'id': u'1053',
                    u'properties': {u'date': 1210377600000,
                                    u'height': 332.0,
                                    u'lng': -122.478504,
                                    u'title': u'San Francisco -  - Golden Gate Bridge',
                                    u'url': u'http://mw2.google.com/mw-panoramio/photos/medium/10085769.jpg',
                                    u'user_id': 949501.0,
                                    u'user_name': u'Adnew',
                                    u'width': 500.0},
                    u'type': u'Feature'},
                   {u'geometry': {u'coordinates': [-122.386322, 37.798798],
                                  u'geodesic': True,
                                  u'type': u'Point'},
                    u'id': u'1340',
                    u'properties': {u'date': 1300147200000,
                                    u'height': 358.0,
                                    u'lng': -122.386322,
                                    u'title': u'Oakland-Bay-Bridge',
                                    u'url': u'http://mw2.google.com/mw-panoramio/photos/medium/49518296.jpg',
                                    u'user_id': 949501.0,
                                    u'user_name': u'Adnew',
                                    u'width': 500.0},
                    u'type': u'Feature'}],
     u'properties': {u'DocID': u'1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo',
                     u'name': u'SF Panoramio Photos +ID'},
     u'type': u'FeatureCollection'}

Note that the request returned a Python dictionary object.


WHERE with an aggregator
^^^^^^^^^^^^^^^^^^^^^^^^

We can also apply an aggregator to the restricted query, e.g. to count the number of rows in the **date** column for entries
of a given **user_name**.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT COUNT(date) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE user_name = Alfred Mueller'
    >>>q = SQL2GEE(sql)
    >>>q.response
    6

WHERE with conditionals and an aggregator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Restrictions can also use comparison operators. For example, we could return the first row from the **url** column where
the **height** of photos was great-than-or-equal-to (>=) 500 pixels.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT FIRST(url) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE height >= 500'
    >>>q = SQL2GEE(sql)
    >>>q.response
    u'http://mw2.google.com/mw-panoramio/photos/medium/1529603.jpg'

Restrictions can be compounded into quite complex statements. For example, we can return the average (AVG) longitude
value from the **lng** column, where the **height** of photos was greater than (>) 400 pixels, and the **width** was
greater-than 400 pixels.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT AVG(lng) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo" WHERE height > 400 AND width > 400'
    >>>q = SQL2GEE(sql)
    >>>q.response
    -122.36732296666668


Operations on Image Data
-------------------------

Sql2gee supports Postgis-like operations on raster (image) data that is publicly accessible in Google's Earth Engine.
Our functions include the ability to subset (clip) images by `geojson <http://geojson.org>`_ data.
If successful, the response of these objects will be a dictionary.

We will demonstrate performing these operations on both a single-band image, **strm90_v4** (which contains 90m
elevation data globally), and **LC81412332013146LGN00** (a multi-band Landasat-8 tile).

Retrieve Image Metadata
^^^^^^^^^^^^^^^^^^^^^^^

To retrieve image metadata, use the ST_METADATA() function. (A refrence to the Postgis version of this operation is
`here <http://postgis.net/docs/RT_ST_MetaData.html>`_.)

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT ST_METADATA() from srtm90_v4'
    >>>q = SQL2GEE(sql)
    >>>q.response
    {u'bands': [{u'crs': u'EPSG:4326',
                 u'crs_transform': [0.000833333333333,
                                    0.0,
                                    -180.0,
                                    0.0,
                                    -0.000833333333333,
                                    60.0],
                 u'data_type': {u'max': 32767,
                                u'min': -32768,
                                u'precision': u'int',
                                u'type': u'PixelType'},
                 u'dimensions': [432000, 144000],
                 u'id': u'elevation'}],
     u'id': u'srtm90_v4',
     u'properties': {u'system:asset_size': 18827626666,
                     u'system:time_end': 951177600000,
                     u'system:time_start': 950227200000},
     u'type': u'Image',
     u'version': 1463778555689000}


Summary Statistics over an Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Summary statistics can be retrieved per-band of Images in the Earth Engine data catalouge via the use of the postgis-like
`ST_SUMMARYSTATS() <http://postgis.net/docs/RT_ST_SummaryStats.html>`_ function, as shown below.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT ST_SUMMARYSTATS() from srtm90_v4'
    >>>q = SQL2GEE(sql)
    >>>q.response
    {u'elevation': {'count': 2747198,
                    'max': 7159,
                    'mean': 689.8474833769903,
                    'min': -415,
                    'stdev': 865.9582784994756,
                    'sum': 1859471136.0274282}}

It is possible to add an area-restriction to the image queries, by passing a geojson polygon or multipolygon object as an
argument to the SQL2GEE class as follows.

Note, in the below example we call a geojson object using a geostore API and the
`Python Requests library <http://docs.python-requests.org/en/master/>`_, but if you happen-to-have a geojson handy, then
you could simply pass that instead and skip lines 1-5.

.. code-block:: python
   :linenos:

    >>>import requests
    >>>gstore = "http://staging-api.globalforestwatch.org/geostore/4531cca6a8ddcf01bccf302b3dd7ae3f"
    >>>r = requests.get(gstore)
    >>>j = r.json()
    >>>j = j.get('data').get('attributes').get('geojson')

    >>>sql = "SELECT ST_SUMMARYSTATS() FROM srtm90_v4"
    >>>q = SQL2GEE(sql, geojson=j)
    {u'elevation': {'count': 118037,
                    'max': 489,
                    'mean': 326.5521573743826,
                    'min': 126,
                    'stdev': 75.69057079693977,
                    'sum': 38545237.0}}


Histogram information over an Image Band
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To return the data required to produce a histogram (bin position and frequency), the postgis-like `ST_HISTOTRAM() <http://postgis.net/docs/manual-dev/RT_ST_Histogram.html>`_ method can be used.
Again, SQL2GEE can be passed a geojson if desired, as in the previous example, to restrict the results to only a specific region (or regions).

.. code-block:: python
   :linenos:

    >>>sql = "SELECT ST_HISTOGRAM() FROM srtm90_v4"
    >>>q = SQL2GEE(sql)
    >>>q.response
    {u'elevation': [[-415.0, 14.0],
                    [-404.94156706507306, 6.0],
                    [-394.88313413014606, 3.0],
                    [-384.8247011952191, 1.0],
                    ...
                    [7128.824701195219, 0.0],
                    [7138.883134130146, 0.0],
                    [7148.941567065073, 0.0]]}

By default, the returned dictionary contains a key for the first band of the specified image. This holds a 2D list, of [(x, y)...n], where n = number of bins.
The x position in the returned list gives the left bin corner, while the y position gives the frequency (counts) for that bin. By default, the
bin number is calculated via the `Freedman-Diaconis rule <https://en.wikipedia.org/wiki/Freedman–Diaconis_rule>`_.
However, `ST_HISTOGRAM() <http://postgis.net/docs/manual-dev/RT_ST_Histogram.html>`_ is designed to be called with arguments, like the POSTGIS version of the function. Currently, the effect of these arguments
is to specify the *band* a user wishes to retrieve, the number of *bins* a user wishes to use in their histogram, and whether or not the user wishes to invert the order
of the returned bins (i.e. return them from largest **bin value** to smallest, instead of smallest-to-largest). Due to imitating the postgis-like nature of these functions,
keyword assignment is not supported, and therefore requests must include all arguments. Additionally, a string `raster` (with no whitespace or commas) must also be given as a first argument. However,
this string does not have any affect on the program: we reccomend simply calling it `raster`, without quotation marks (as in the below example).
As in the POSTGIS documentation the arguments for ST_HISTOGRAM are as follows: ST_Histogram(*raster* **rast**, *integer* **nband**, *integer* **bins**, *boolean* **right**).

For example, we may retrieve histogram information for `B2` of a Landast-8 tile, divided into 10 bins, ordered from lowest bin value to largest, as follows:

.. code-block:: python
   :linenos:

    >>>sql = "SELECT ST_HISTOGRAM(raster, B2, 10, true) FROM LC81412332013146LGN00"
    >>>q = SQL2GEE(sql)
    >>>q.response
    {'B2': [[6146.0, 1811731.7647058824],
            [7033.9, 1631439.6901960785],
            [7921.8, 2552924.3843137254],
            [8809.7, 3739584.364705882],
            [9697.6, 157919.0],
            [10585.5, 60484.25882352941],
            [11473.4, 28978.003921568627],
            [12361.3, 10498.752941176472],
            [13249.2, 2731.4980392156863],
            [14137.099999999999, 465.0]]}

If the band names of an image are unknown, you may use integer values as an index: E.g. instead of entering `B2` in the previous example
you could have entered the integer `2`. Alternatively, you may discover the keys of the bands (band names) via a separate query to the image using ST_METADATA(), as shown below.

.. code-block:: python
   :linenos:

    >>>sql = "SELECT ST_METADATA() FROM LC81412332013146LGN00"
    >>>q = SQL2GEE(sql)
    >>>q.response
    >>>for band in r.response['bands']:
    >>>    print(band['id'])
    B1
    B2
    B3
    B4
    B5
    B6
    B7
    B8
    B9
    B10
    B11
    BQA