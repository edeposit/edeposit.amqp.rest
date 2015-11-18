#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from BTrees.OOBTree import OOBTree

import transaction
from zeo_connector import ZEOConfWrapper


# Functions & classes =========================================================
class DatabaseHandler(object):
    """
    Define interfaces to the database, configuration and so on.

    Attributes:
        conf_path (str): Path to the ZEO client XML configuration.
        project_key (str): Project key, which is used to access ZEO.
        zeo (obj): :class:`.ZEOConfWrapper` database object.
    """
    def __init__(self, conf_path, project_key):
        self.conf_path = conf_path
        self.project_key = project_key

        self.zeo = None
        self._reload_zeo()

    def _reload_zeo(self):
        self.zeo = ZEOConfWrapper(
            conf_path=self.conf_path,
            project_key=self.project_key
        )

    def _get_key_or_create(self, key, obj_type=OOBTree):
        with transaction.manager:
            key_obj = self.zeo.get(key, None)

            if key_obj is None:
                key_obj = obj_type()
                self.zeo[key] = key_obj

            return key_obj
