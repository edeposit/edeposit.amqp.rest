#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from BTrees.OOBTree import OOBTree

import transaction
from zeo_connector import ZEOConfWrapper


# Variables ===================================================================
# Functions & classes =========================================================
def create_hash(password):
    return str(hash(password))  # TODO: change to cryptographic hashing function


class DatabaseHandler(object):
    def __init__(self, conf_path, project_key):
        self.conf_path = conf_path
        self.project_key = project_key

        self.users_key = "users"

        self.zeo = ZEOConfWrapper(conf_path, project_key)

        # read the proper indexes
        self.users = self._get_key_or_create(self.users_key)

    def _get_key_or_create(self, key, obj_type=OOBTree):
        with transaction.manager:
            key_obj = self.zeo.get(key, None)

            if key_obj is None:
                key_obj = obj_type()
                self.zeo[key] = key_obj

            return key_obj

    def add_user(self, username, pw_hash):
        with transaction.manager:
            self.users[username] = pw_hash

    def remove_user(self, username):
        with transaction.manager:
            del self.users[username]

    def is_valid_user(self, username, password, hashing_mechanism=create_hash):
        with transaction.manager:
            pass_hash = self.users.get(username, None)

        if pass_hash is None:
            return False

        return create_hash(password) == pass_hash

    def save_status_update(self, status):
        pass

    def query_status(self, book_id):
        pass
