#!/usr/bin/python -p

import logging
import yaml

lg = logging.getLogger(__name__)
input_cache = {}


def load_config(input_defaults=None, input_file=None):
    """
    Load config parameters either from file or stdin
    """

    if input_file:
        lg.debug("Loading default inputs from yaml file {}".format(input_file))
        try:
            with open(input_file) as f:
                ifile = yaml.full_load(f)
        except IOError as e:
            lg.error("Can't open config file {0}: {1}".format(input_file, e))
            raise

        for key, value in ifile.items():
            if not isinstance(value, str):
                lg.error("Input key {0} has not string-typed value ({1}), ignoring".format(key, value))
                continue
            input_cache[key] = value

    if input_defaults:
        for input in input_defaults:
            try:
                key, value = input.split('=')
            except ValueError:
                lg.error("Submitted input value {} is not a valid key=pair, skipping".format(input))
                continue
            input_cache[key] = value

    return input_cache


def load_measurements(input_file):
    lg.debug("Loading measurements list from file {}".format(input_file))
    try:
        with open(input_file) as f:
            mlist = f.read().splitlines()
    except IOError as e:
        lg.error("Can't open config file {0}: {1}".format(input_file, e))
        raise

    return mlist

# print(load_config(input_file='secrets.yml')["loxone::host"])
