#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import transaction

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler


class CacheHandler(DatabaseHandler):
    """
    """
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.cache_key = "cache"
        self.users = self._get_key_or_create(self.cache_key)

    def add_upload_request(metadata, bds_id):
        pass

    def get_upload_request():
        pass
