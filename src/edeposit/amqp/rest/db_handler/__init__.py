#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import thread
import asyncore

import transaction

from ZODB import DB
from ZODB.config import storageFromFile
from ZODB.POSException import ConnectionStateError

from BTrees.OOBTree import OOBTree


# Variables ===================================================================
ASYNCORE_RUNNING = False


# Functions & classes =========================================================
def init_zeo():
    if ASYNCORE_RUNNING:
        return

    def run_asyncore_loop():
        asyncore.loop()

    thread.start_new_thread(run_asyncore_loop, ())

    global ASYNCORE_RUNNING
    ASYNCORE_RUNNING = True


class ZEOWrapper(object):
    def __init__(self, conf_path, project_key):
        self.conf_path = conf_path
        self.project_key = project_key
        self.default_type = OOBTree

        self._db_root = None
        self._connection = None

        init_zeo()
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
            with transaction.manager:
                dbroot[self.project_key] = self.default_type()

        self._db_root = dbroot[self.project_key]

    def sync(self):
        self._connection.sync()

    def __getitem__(self, key):
        try:
            return self._db_root[key]
        except ConnectionStateError:
            self._on_close_callback()

        return self._db_root[key]

    def __setitem__(self, key, val):
        try:
            self._db_root[key] = val
        except ConnectionStateError:
            self._on_close_callback()

        self._db_root[key] = val
