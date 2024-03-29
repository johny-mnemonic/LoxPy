#!/usr/bin/python -p

# import libs for Loxone connection
import requests
from requests.auth import HTTPBasicAuth
import urllib2
from base64 import b64encode
import urllib3

import json

# Initialize logging
import logging
lg = logging.getLogger(__name__)


def get_req(url, user, password):
    try:
        myResponse = requests.get(
            url, auth=HTTPBasicAuth(user, password), verify=True, timeout=(2.0, 7.0)
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout ) as e:
        lg.error("Connection to Miniserver failed with: {}".format(e))
        return None

    if (myResponse.ok):
        return myResponse.json()
    else:
        lg.error("Connection to Miniserver failed \
        with http status code: {}".format(myResponse.status_code))
        return None


def get_url2(url, user, password):
    try:
        request = urllib2.Request(url)
        request.add_header(
            'Authorization', 'Basic ' + b64encode(user + ':' + password)
        )
        handler = urllib2.urlopen(request, timeout=7)
    except urllib2.HTTPError as e:
        lg.error("Connection to Miniserver failed with: {}".format(e))
        return None

    if (handler.code == 200):
        return json.loads(handler.read())
    else:
        lg.error("Connection to Miniserver failed \
        with http status code: {}".format(handler.code))
        return None


def get_url3(url, user, password):
    try:
        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth=user + ':' + password)
        response = http.request('GET', url, headers=headers, timeout=Timeout(connect=2.0, read=7.0))
    except urllib3.exceptions.NewConnectionError as e:
        lg.error("Connection to Miniserver failed with: {}".format(e))
        return None

    if (response.status == 200):
        return json.loads(response.data)
    else:
        lg.error("Connection to Miniserver failed \
        with http status code: {}".format(response.status))
        return None


def strip_units(value):
    while value:
        try:
            float(value)
            break
        except ValueError:
            value = value[:-1]
    return value


def loxclient(
    host, user, password, action='state', obj=None, strip=False, lib='requests'
    ):
    # Set Loxone URL
    if obj is None:
        url = "http://{0}/jdev/sps/{1}".format(host, action)
    elif '/' in obj:
        url = "http://{0}/jdev/{1}".format(host, obj)
    elif obj in ['sys', 'cfg', 'lan', 'bus', 'task0']:
        url = "http://{0}/jdev/{1}/{2}".format(host, obj, action)
    else:
        url = "http://{0}/jdev/sps/io/{1}/{2}".format(host, obj, action)
    lg.debug("Loxone URL is: {}".format(url))

    # Get Json data from Miniserver
    #obj = 'Dummy_Object' if obj is None else obj
    #mock_data = str('{"LL": { "control": "dev/sps/io/' + obj + '/state", "value": "531.68", "Code": "200"}}')
    #jData = json.loads(mock_data)
    get = {'requests': get_req, 'urllib2': get_url2, 'urllib3': get_url3}
    jData = get[lib](url, user, password)
    if jData is None:
        # Getting the data failed, bailing out
        return None
    lg.debug("The response json content is: {}".format(jData))

    # Check return code inside the json.
    # If it's not 200, response probably doesn't contain what we asked for.
    if jData['LL']['Code'] != '200':
        lg.error(
            "Miniserver returned error code: {}".format(jData['LL']['Code'])
        )
        return None

    # Get the value from json response and optionally strip it from units.
    value = jData['LL']['value']
    if strip:
        value = float(strip_units(value))
        lg.debug("The requested value is: {}".format(value))
    else:
        # Do not crash on non-ASCII chars (i.e. Czech).
        # Convert it into UTF8 string for logger first.
        lg.debug("The requested value is: {}".format(value.encode("utf-8")))

    return value
