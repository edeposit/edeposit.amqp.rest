#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import transaction

from database_handler import DatabaseHandler


# Functions & classes =========================================================
class StatusHandler(DatabaseHandler):
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.status_db_key = "status"
        self.status_db = self._get_key_or_create(self.status_db_key)

    def register_status_tracking(self, username, rest_id):
        pass

    def save_status_update(self, status_update):
        pass

    def query_status(self, username, rest_id):
        pass
