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
This data has a column called **lng**, each row of 'which contains a value for Longitude where a photo was taken.

We may request the first row of **lng** data from the table as follows.

.. code-block:: python
   :linenos:

    >>>sql = 'SELECT FIRST(lng) from "ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo"'
    >>>q = SQL2GEE(sql)
    >>>q.response
    -122.199705

Note that the actual response to our query is returned via the ``q.response`` property.

We may count the number of rows of **lng** data in the table as follows.

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