Supported SQL and Postgis Syntax
================================

Select
    Currently only with one table: joins are not supported.

FROM
    Data source (either `Google Fusion table ID <https://sites.google.com/site/fusiontablestalks/stories>`_, or `Earth Engine Image ID <https://earthengine.google.com/datasets/>`_).

Where
    * >, <, >=, <=, <>, =
    * LIKE, NOT LIKE
    * NOT
    * AND, OR
    * IN
    * IS

Feature Collection Functions
    * COUNT
    * SUM
    * AVG
    * MAX
    * MIN
    * FIRST
    * STDEV
    * VAR
    * LIMIT

Postgis-like Raster Functions
    * ST_METADATA
    * ST_HISTOGRAM
    * ST_SUMMARYSTATS

We will add support for more language features as time goes on.