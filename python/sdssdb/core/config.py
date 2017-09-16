#!/usr/bin/env python
# encoding: utf-8
#
# config.py
#
# Created by José Sánchez-Gallego on 18 Jun 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import yaml

if sys.version_info > (3, 0):
    import pathlib
else:
    import pathlib2 as pathlib


def merge(user, default):
    """Merges a user configuration with the default one."""

    if not user:
        return default

    if isinstance(user, dict) and isinstance(default, dict):
        for kk, vv in default.items():
            if kk not in user:
                user[kk] = vv
            else:
                user[kk] = merge(user[kk], vv)

    return user


def get_config():
    """Returns a dictionary object with sdss_peewee's configuration options."""

    user_path = pathlib.Path.home() / '.sdssdb'
    user = user_path.exists() and yaml.load(open(str(user_path), 'r'))

    default_path = pathlib.Path(__file__).parents[3] / 'etc/sdssdb.yaml'
    default = yaml.load(open(str(default_path), 'r'))

    return merge(user, default)
