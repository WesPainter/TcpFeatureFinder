import os
import sys

def get_list_from_config(config, section, param):
    '''
    Given a read in config object, return a list of items from a section and parameter.

    Config item will be of the form:
    [section]
    param = 
        item1
        item2
        ...
        itemN

    '''
    raw = config.get(section, param)
    items = list(filter(
                None, [item.strip() for item in raw.splitlines()]))
    return items
