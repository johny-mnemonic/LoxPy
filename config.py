#!/usr/bin/python

import logging
import yaml

lg = logging.getLogger(__name__)
input_cache = {}

def load_config(input_defaults=None, input_file=None):
    """
    Load config parameters either from file or stdin
    """

    if input_file:
        lg.debug("Loading default inputs from yaml file %s" % input_file)
        try:
            cf = open(input_file)
            ifile = yaml.load(cf)
        except IOError as e:
            lg.error("Can't open config file %s: %s" % (input_file, e))
            raise
        finally:
            cf.close()

        for key, value in ifile.items():
            if not isinstance(value, str):
                lg.error("Input key %s has not string-typed value (%s), ignoring" % (key, value))
                continue
            input_cache[key] = value

    if input_defaults:
        for input in input_defaults:
            try:
                key, value = input.split('=')
            except ValueError:
                lg.error("Submitted input value %s is not a valid key=pair, skipping" % input)
                continue
            input_cache[key] = value

    return input_cache

#print(load_config(input_file='secrets.yml')["loxone::host"])
