#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from ZODB import DB
from ZEO import ClientStorage

from zeo_wrapper_prototype import ZEOWrapperPrototype


# Functions & classes =========================================================
class ZEOWrapper(ZEOWrapperPrototype):
    """
    ZEO wrapper based on ZEO client XML configuration file.

    Attributes:
        conf_path (str): Path to the configuration file.
        project_key (str): Project key, under which will this object access the
            ZEO structure.
        default_type (obj): Default data object used for root, if the root
            wasn't already created in ZEO.
    """
    def __init__(self, server, port, project_key, run_asyncore_thread=True):
        """
        Initialize the object.

        Args:
            conf_path (str): See :attr:`conf_path`.
            project_key (str): See :attr:`project_key`.
            run_asyncore_thread (bool, default True): Run external asyncore
                thread, which handles connections to database? Default True.
        """
        self.server = server
        self.port = port

        super(ZEOWrapper, self).__init__(
            project_key=project_key,
            run_asyncore_thread=run_asyncore_thread,
        )

    def _get_db(self):
        """
        Open the connection to the database based on the configuration file.
        """
        return DB(
            ClientStorage.ClientStorage((self.server, self.port))
        )
