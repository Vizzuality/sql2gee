.. sql2gee documentation master file, created by
   sphinx-quickstart on Mon Jan 23 12:01:20 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sql2gee's documentation!
===================================

The `sql2gee library<https://github.com/Vizzuality/sql2gee>`_ is designed to convert SQL (and `Postgis <http://postgis.net>`_)-like queries into commands to be executed on
`Google's Earth Engine <https://earthengine.google.com>`_, using their `Python API <https://developers.google.com/earth-engine/python_install>`_.

This library allows you to create SQL queries against either vector data or rasters:
If you desire vector data, you may use `Google's Fusion Tables <https://sites.google.com/site/fusiontablestalks/stories>`_
as a data source (SQL TABLE argument) provided it has geo-spatial data (e.g. `ft:1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo <https://fusiontables.google.com/data?docid=1qpKIcYQMBsXLA9RLWCaV9D0Hus2cMQHhI-ViKHo#rows:id=1>`_).
If raster (image) data is desired, you may use any Image resource from the `Earth Engine data catalogue <https://earthengine.google.com/datasets/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   supportedsyntax
   gettingstarted
   sql2gee
   support

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
