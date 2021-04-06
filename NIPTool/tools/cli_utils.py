import json
import yaml
import logging
import os
import pathlib
import copy
import collections

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


def convert_dot(string):
    """
    replaces dot with underscore
    """
    return string.replace(".", "_")


def add_doc(docstring):
    """
    A decorator for adding docstring. Taken shamelessly from stackexchange.
    """

    def document(func):
        func.__doc__ = docstring
        return func

    return document


def dict_replace_dot(obj):
    """
    recursively replace all dots in json.load keys.
    """
    if isinstance(obj, dict):
        for key in obj.keys():
            obj[convert_dot(key)] = obj.pop(key)
            if isinstance(obj[convert_dot(key)], dict) or isinstance(obj[convert_dot(key)], list):
                obj[convert_dot(key)] = dict_replace_dot(obj[convert_dot(key)])
    elif isinstance(obj, list):
        for item in obj:
            item = dict_replace_dot(item)
    return obj


def json_read(fname):
    """
    Reads JSON file and returns dictionary. Returns error if can't read.
    """

    try:
        with open(fname, "r") as f:
            analysis_conf = json.load(f, object_hook=dict_replace_dot)
            return analysis_conf
    except:
        LOG.warning("Input config is not JSON")
        return False


def yaml_read(fname):
    """
    Reads YAML file and returns dictionary. Returns error if can't read.
    """

    try:
        with open(fname, "r") as f:
            analysis_conf = yaml.load(f)
            return analysis_conf
    except:
        LOG.warning("Input config is not YAML")
        return False


def check_file(fname):
    """
    Check file exists and readable.
    """

    path = pathlib.Path(fname)

    if not path.exists() or not path.is_file():
        LOG.error("File not found or input is not a file.")
        raise FileNotFoundError


def concat_dict_keys(my_dict: dict, key_name="", out_key_list=list()):
    """
    Recursively create a list of key:key1,key2 from a nested dictionary
    """

    if isinstance(my_dict, dict):

        if key_name != "":
            out_key_list.append(key_name + ":" + ", ".join(list(my_dict.keys())))

        for k in my_dict.keys():
            concat_dict_keys(my_dict[k], key_name=k, out_key_list=out_key_list)

    return out_key_list


def recursive_default_dict():
    """
    Recursivly create defaultdict.
    """
    return collections.defaultdict(recursive_default_dict)


def convert_defaultdict_to_regular_dict(inputdict: dict):
    """
    Recursively convert defaultdict to dict.
    """
    if isinstance(inputdict, collections.defaultdict):
        inputdict = {
            key: convert_defaultdict_to_regular_dict(value) for key, value in inputdict.items()
        }
    return inputdict
