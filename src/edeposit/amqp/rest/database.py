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

        self.zeo = ZEOConfWrapper(conf_path, project_key)

    def _get_key_or_create(self, key, obj_type=OOBTree):
        with transaction.manager:
            key_obj = self.zeo.get(key, None)

            if key_obj is None:
                key_obj = obj_type()
                self.zeo[key] = key_obj

            return key_obj


class UserHandler(DatabaseHandler):
    """
    User database.

    Attributes:
        users_key (str): Key which is used to access database.
        users (obj): Dict-like object in ZEO.
    """
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.users_key = "users"
        self.users = self._get_key_or_create(self.users_key)

    def add_user(self, username, pw_hash):
        """
        Add new user / update user's details.

        Args:
            username (str): Username of the new user.
            pw_hash (str): Hash of the user'r password. See :func:`create_hash`
                for details.
        """
        with transaction.manager:
            self.users[username] = pw_hash

    def remove_user(self, username):
        """
        Remove `username` from the database.

        Args:
            username (str): Username of the new user.
        """
        with transaction.manager:
            del self.users[username]

    def is_valid_user_hashed(self, username, hashed_password):
        """
        Check whether `username` and user's `hashed_password` is valid.

        Args:
            username (str): Username.
            hashed_password (str): Cleantext version of the password.

        Returns:
            bool: True if valid.
        """
        with transaction.manager:
            stored_pass_hash = self.users.get(username, None)

        if stored_pass_hash is None:
            return False

        return hashed_password == stored_pass_hash

    def is_valid_user(self, username, password, hashing_mechanism=create_hash):
        """
        Check whether the username:password pair is valid or not.

        Args:
            username (str): Username.
            password (str): Cleantext version of the password.
            hashing_mechanism (fn ref): Hashing function. Default
                :func:`create_hash`.

        Returns:
            bool: True if valid.
        """
        return self.is_valid_user_hashed(
            username=username,
            hashed_password=hashing_mechanism(password)
        )


class StatusHandler(DatabaseHandler):
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.status_key = "status"
        self.status = self._get_key_or_create(self.status_key)

    def save_status_update(self, status):
        pass

    def query_status(self, book_id):
        pass
