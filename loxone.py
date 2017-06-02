#!/usr/bin/python -p

# import libs for Loxone connection
import requests
from requests.auth import HTTPBasicAuth

import json

# Initialize logging
import logging
lg = logging.getLogger(__name__)


def get_req(url, user, password):
    try:
        myResponse = requests.get(url, auth=HTTPBasicAuth(user, password), verify=True)
    except requests.exceptions.ConnectionError as e:
        lg.error("Connection to Miniserver failed with: {}".format(e))
        return None

    if (myResponse.ok):
        return myResponse.json()
    else:
        lg.error("Connection to Miniserver failed with http status code: {}".format(myResponse.status_code))
        return None


def strip_units(value):
    while value:
        try:
            float(value)
            break
        except ValueError:
            value = value[:-1]
    return value


def loxclient(host, user, password, action='state', obj=None, strip=False):
    # Set Loxone URL
    if obj is None:
        url = "http://{0}/jdev/sps/{1}".format(host, action)
    else:
        url = "http://{0}/jdev/sps/io/{2}/{1}".format(host, action, obj)
    lg.debug("Loxone URL is: {}".format(url))
    # Get Json data from Miniserver
    mock_data = str('{"LL": { "control": "dev/sps/io/LightSensor_Pracovna/state", "value": "531.68", "Code": "200"}}')
    jData = json.loads(mock_data)
    #jData = get_req(url, user, password)
    lg.debug("The response json content is: {}".format(jData))
    if jData['LL']['Code'] != '200':
        lg.error("Miniserver returned error code: {}".format(jData['LL']['Code']))
        return None
    value = jData['LL']['value']
    if strip:
        value = float(strip_units(value))
        lg.debug("The requested value is: {}".format(value))
    else:
        lg.debug("The requested value is: {}".format(value.encode().decode()))

    return value
