#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from zeo_connector import ZEOConfWrapper


# Variables ===================================================================



# Functions & classes =========================================================
class DatabaseHandler(object):
    def __init__(self, conf_path, project_key):
        self.conf_path = conf_path
        self.project_key = project_key

        self.zeo = ZEOConfWrapper(conf_path, project_key)

    def add_user(self, username, pw_hash):
        pass

    def remove_user(self, username):
        pass

    def save_status_update(self, status):
        pass

    def is_valid_user(self, username, password):
        pass

    def query_status(self, book_id):
        pass
