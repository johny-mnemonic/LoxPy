#!/usr/bin/python

import config

import argparse
from loxone import loxclient
#import json

parser = argparse.ArgumentParser(description="Simple Loxone RESTful client. Without paramteres it checks Miniserver state")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Enable verbose output")
parser.add_argument("-d", "--debug", action="store_true",
                    help="Enable debug output")
parser.add_argument("-o", "--object",
                    help="Loxone object to query. Could be name or UUID")
parser.add_argument("-a", "--action", default='state',
                    help="Action to do with the object. Default is 'state'")
args = parser.parse_args()

# Initialize logging
import logging
lg = logging.getLogger(__name__)
if args.verbose:
    #print("Verbose output turned on")
    loglvl = logging.INFO
elif args.debug:
    #print("Debug output turned on")
    loglvl = logging.DEBUG
else:
    loglvl = logging.ERROR
logging.basicConfig(
    # filename=args.log_file,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
    level=loglvl
    )

# Read configuration from config file
config_cache=config.load_config(input_file="secrets.yml")
loxusr = config_cache["loxone::user"]
loxpass = config_cache["loxone::password"]
loxhost = config_cache["loxone::host"]

# debug default
args.object = "LightSensor_Pracovna"

if args.object == None:
    url = 'http://loxone/jdev/sps/state'
else:
    url = 'http://' + loxhost + '/jdev/sps/io/' + args.object + '/' + args.action


def get_req():
    import requests
    from requests.auth import HTTPBasicAuth
    myResponse = requests.get(url, auth=HTTPBasicAuth(loxusr,loxpass), verify=True)
    if args.debug:
        print('Http return code is: {0}'.format(myResponse.status_code))
    # For successful API call, response code will be 200 (OK)
    if (myResponse.ok):
        if args.debug:
            print("The response raw content is:")
            print(myResponse.text)
        return myResponse.json()
    else:
        # If response code is not ok (200), print the resulting
        #http error code with description
        myResponse.raise_for_status()


def get_url2():
    import urllib2
    from base64 import b64encode
    import json
    try:
        request = urllib2.Request(url)
        request.add_header('Authorization', 'Basic ' + b64encode( loxusr + ':' + loxpass))
        handler = urllib2.urlopen(request)
    except:
        #lg.error("Connection to Miniserver failed with: {}".format(e))
        print("Connection to Miniserver failed")
        return None
    if args.debug:
        print('Http return code is: {0}'.format(handler.code))
    if (handler.code == 200 ):
        try:
            rdata = handler.read()
            jdata = json.loads(rdata)
            #jdata = json.loads(handler.read())
        except:
            print("Failed to parse Json")
            return None
        if args.debug:
            print("The response raw content is:")
            print(rdata)
        return jdata
    else:
        return None

def get_url3():
    import urllib3
    import json
    try:
        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth=loxusr + ':' + loxpass)
        response = http.request('GET', url, headers = headers)
    except:
        #lg.error("Connection to Miniserver failed with: {}".format(e))
        print("Connection to Miniserver failed")
        return None
    if args.debug:
        print('Http return code is: {0}'.format(response.status))
    if (response.status == 200 ):
        if args.debug:
            print("The response raw content is:")
            print(response.data)
        try:
            jdata = json.loads(response.data)
        except:
            print("Failed to parse Json")
            return None
        return jdata
    else:
        print('Wrong return code')
        return None

if __name__ == '__main__':
    #from timeit import Timer
    #t_urllib2 = Timer("get_url2()", "from __main__ import get_url2")
    #print 'urllib2: {0}'.format(t_urllib2.timeit(number=1))
    #t_urllib3 = Timer("get_url3()", "from __main__ import get_url3")
    #print 'urllib3: {0}'.format(t_urllib3.timeit(number=1))
    #t_req = Timer("get_req()", "from __main__ import get_req")
    #print 'requests: {0}'.format(t_req.timeit(number=1))

    #jData = get_url2()
    #mock_data = str('{"LL": { "control": "dev/sps/io/LightSensor_Pracovna/state", "value": "531.68", "Code": "200"}}')
    #print(type(mock_data))
    #jData = json.loads(mock_data)
    #print(type(jData))
    #if args.debug:
     #   print("The response json contains {0} properties".format(len(jData)))
      #  print("The response json content is:")
       # print(jData)
    # value = jData['LL']['value']
    lg.debug("Calling loxclient action '{0}' for '{1}'".format(args.action, args.object))
    value = loxclient(loxhost, loxusr, loxpass, args.action, args.object, strip=False)
    if args.object == None:
        if value == '1':
            print("Miniserver is booting")
        elif value == '2':
            print("Miniserver has loaded the program")
        elif value == '3':
            print("Miniserver has started")
        elif value == '4':
            print("Loxone link has started")
        elif value == '5':
            print("Miniserver is running")
        elif value == '6':
            print("Miniserver state is changing")
        elif value == '7':
            print("Miniserver is in error state")
        elif value == '8':
            print("Miniserver is updating")
    elif args.verbose or args.debug:
        lg.info("Value of {} is {} ".format(args.object,value))
    else:
        print(value)


