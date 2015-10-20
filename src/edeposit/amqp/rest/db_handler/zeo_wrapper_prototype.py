#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import thread
import asyncore

import transaction
from ZODB.POSException import ConnectionStateError
from BTrees.OOBTree import OOBTree


# Variables ===================================================================
ASYNCORE_RUNNING = False


# Functions & classes =========================================================
def _init_zeo():
    """
    Start asyncore thread
    """
    if not ASYNCORE_RUNNING:
        def _run_asyncore_loop():
            asyncore.loop()

        thread.start_new_thread(_run_asyncore_loop, ())

        global ASYNCORE_RUNNING
        ASYNCORE_RUNNING = True


class ZEOWrapperPrototype(object):
    """
    ZEO wrapper prototype baseclass.

    Attributes:
        project_key (str): Project key, under which will this object access the
            ZEO structure.
        default_type (obj): Default data object used for root, if the root
            wasn't already created in ZEO.
    """
    def __init__(self, project_key, run_asyncore_thread=True):
        """
        Initialize the object.

        Args:
            conf_path (str): See :attr:`conf_path`.
            project_key (str): See :attr:`project_key`.
            run_asyncore_thread (bool, default True): Run external asyncore
                thread, which handles connections to database? Default True.
        """
        self.project_key = project_key
        self.default_type = OOBTree

        self._db_root = None  # Reference to the root of the database.
        self._connection = None  #: Internal handler for the ZEO connection.

        if run_asyncore_thread:
            _init_zeo()

        self._open_connection()
        self._init_zeo_root()

    def _on_close_callback(self):
        """
        When the connection is closed, open it again and get new reference to
        ZEO root.
        """
        self._open_connection()
        self._init_zeo_root()

    def _get_db(self):
        """
        This should return the ZODB database object.
        """
        raise NotImplementedError("._get_db() is not implemented yet.")

    def _open_connection(self):
        """
        Open the connection to the database based on the configuration file.
        """
        db = self._get_db()
        self._connection = db.open()

        self._connection.onCloseCallback(self._on_close_callback)

    def _init_zeo_root(self, attempts=3):
        """
        Get and initialize the ZEO root object.

        Args:
            attempts (int, default 3): How many times to try, if the connection
                was lost.
        """
        try:
            dbroot = self._connection.root()
        except ConnectionStateError:
            if attempts <= 0:
                raise

            self._open_connection()
            return self._init_zeo_root(attempts=attempts-1)

        # init the root, if it wasn't already declared
        if self.project_key not in dbroot:
            with transaction.manager:
                dbroot[self.project_key] = self.default_type()

        self._db_root = dbroot[self.project_key]

    def sync(self):
        """
        Sync the connection.

        Warning:
            Don't use this method, if you are in the middle of transaction, or
            the transaction will be aborted.

        Note:
            You don't have to use this when you set :attr:`run_asyncore_thread`
            to ``True``.
        """
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
