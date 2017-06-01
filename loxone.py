#!/usr/bin/python -p

# import libs for Loxone connection
import requests
from requests.auth import HTTPBasicAuth

# Initialize logging
import logging
lg = logging.getLogger(__name__)


def strip_units(value):
    while value:
        try:
            float(value)
            break
        except ValueError:
            value = value[:-1]
    return value


def loxclient(host, user, password, action='state', obj=None, strip=False):
    value = None
    # Set Loxone URL
    if obj is None:
        url = "http://{0}/jdev/sps/{1}".format(host, action)
    else:
        url = "http://{0}/jdev/sps/io/{2}/{1}".format(host, action, obj)
    lg.debug("Loxone URL is: {}".format(url))
    try:
        myResponse = requests.get(url, auth=HTTPBasicAuth(user, password), verify=True)
    except requests.exceptions.ConnectionError as e:
        lg.error("Connection to Miniserver failed with: {}".format(e))
        return value

    if (myResponse.ok):
        jData = myResponse.json()
        lg.debug("The response json content is: {}".format(jData))
        if jData['LL']['Code'] != '200':
            lg.error("Miniserver returned error code: {}".format(jData['LL']['Code']))
            return value
        value = jData['LL']['value']
        if strip:
            value = float(strip_units(value))
            lg.debug("The requested value is: {}".format(value))
        else:
            lg.debug("The requested value is: {}".format(value.encode().decode()))
    else:
        lg.error("Connection to Miniserver failed with http status code: {}".format(myResponse.status_code))
        return value

    return value
