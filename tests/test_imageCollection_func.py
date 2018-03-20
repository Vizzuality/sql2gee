import numpy as np
import requests
import sys
import pytest
from sql2gee import SQL2GEE
from sql2gee.utils.jsonSql import JsonSql
import ee

#Quick hack, if using a local mac, assume you can initilise using the below...
if sys.platform == 'darwin':
    ee.Initialize()
else:
    # Else, assume you have an EE_private_key environment variable with authorisation, as on Travis-CI
    service_account = '390573081381-lm51tabsc8q8b33ik497hc66qcmbj11d@developer.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './privatekey.pem')
    ee.Initialize(credentials, 'https://earthengine.googleapis.com')

def test_metadata_icollection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json())
    response = 'ImageCollection'
    assert q.metadata['type'] == response, "BASIC COUNT query incorrect"
    return

def test_icollection_query():
    sql = "select * from 'IDAHO_EPSCOR/GRIDMET' limit 2"
    q = SQL2GEE(JsonSql(sql).to_json()).response()
    response = 'Image'
    assert len(q) == 2, "BASIC COUNT query incorrect"
    return
