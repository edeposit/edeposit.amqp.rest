#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import transaction

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler


# Functions & classes =========================================================
def create_hash(password):
    return str(hash(password))  # TODO: change to cryptographic hashing function


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

    @transaction_manager
    def add_user(self, username, pw_hash):
        """
        Add new user / update user's details.

        Args:
            username (str): Username of the new user.
            pw_hash (str): Hash of the user'r password. See :func:`create_hash`
                for details.
        """
        self.users[username] = pw_hash

    @transaction_manager
    def remove_user(self, username):
        """
        Remove `username` from the database.

        Args:
            username (str): Username of the new user.
        """
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

    @transaction_manager
    def is_registered(self, username):
        """
        Is the `username` registered in system?

        Args:
            username (str): User's name. Case sensitive.

        Returns:
            bool: True if the user is registered.
        """
        return username in self.users
