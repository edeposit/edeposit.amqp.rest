#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path

from ZODB import DB
from ZODB.config import storageFromFile
from ZODB.POSException import ConnectionStateError

from BTrees.OOBTree import OOBTree


# Variables ===================================================================
# Functions & classes =========================================================
class ZEOWrapper(object):
    def __init__(self, conf_path, project_key):
        self.conf_path = conf_path
        self.project_key = project_key
        self.default_type = OOBTree

        self._db_root = None
        self._connection = None
        self._open_connection()
        self._get_zeo_root()

    def _on_close_callback(self):
        self._open_connection()
        self._get_zeo_root()

    def _open_connection(self):
        db = DB(storageFromFile(open(self.conf_path)))
        self._connection = db.open()

        self._connection.onCloseCallback(self._on_close_callback)

    def _get_zeo_root(self, counter=3):
        try:
            dbroot = self._connection.root()
        except ConnectionStateError:
            if counter <= 0:
                raise

            self._open_connection()
            return self._get_zeo_root(counter=counter-1)

        if self.project_key not in dbroot:
            dbroot[self.project_key] = self.default_type()

        self._db_root = dbroot[self.project_key]

    def sync(self):
        self._connection.sync()

    def _get_item(self, key):
        self.sync()

        if not self._db_root.get(key, None):
            self._db_root[key] = self.default_type()
            self.sync()

        return self._db_root[key]

    def _set_item(self, key, val):
        self.sync()
        self._db_root[key] = val
        self.sync()

    def __getitem__(self, key):
        try:
            return self._get_item(key)
        except ConnectionStateError:
            self._on_close_callback()

        return self._get_item(key)

    def __setitem__(self, key, val):
        try:
            return self._set_item(key, val)
        except ConnectionStateError:
            self._on_close_callback()

        return self._set_item(key, val)
