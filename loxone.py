#!/usr/bin/python

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

def loxclient(host, user, password, action='state', obj=None):
    # Set Loxone URL
    if obj == None:
        url = "http://{0}/jdev/sps/{1}".format(host, action)
    else:
        url = "http://{0}/jdev/sps/io/{2}/{1}".format(host, action, obj)
    lg.debug("Loxone URL is: {}".format(url))

    myResponse = requests.get(url, auth=HTTPBasicAuth(user, password), verify=True)
    if (myResponse.ok):
        jData = myResponse.json()
        lg.debug("The response json content is: {}".format(jData))
        value = strip_units(jData['LL']['value'])
        lg.debug("The requested value is: {}".format(value))
    else:
        myResponse.raise_for_status()

    return value
