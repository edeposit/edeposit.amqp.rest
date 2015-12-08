#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import bcrypt
import transaction

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler

from ..settings import PROJECT_KEY
from ..settings import ZEO_CLIENT_CONF_FILE


# Functions & classes =========================================================
def create_hash(password):
    """
    Compute the hash using bcrypt.

    Args:
        password (str): Password which will be hashed.

    Returns:
        str: Hashed password.
    """
    return bcrypt.hashpw(str(password), bcrypt.gensalt())


class UserHandler(DatabaseHandler):
    """
    User database.

    Attributes:
        users_key (str): Key which is used to access database.
        users (obj): Dict-like object in ZEO.
    """
    def __init__(self, conf_path=ZEO_CLIENT_CONF_FILE,
                 project_key=PROJECT_KEY):
        """
        Constructor.

        Args:
            conf_path (str): Path to the file with ZEO client configuration.
                Default :attr:`.ZEO_CLIENT_CONF_FILE`.
            project_key (str): Key used to access the ZEO `root`. Default
                :attr:`.PROJECT_KEY`.
        """
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

    def is_valid_user(self, username, password):
        """
        Check whether `username` and user's `hashed_password` is valid.

        Args:
            username (str): Username.
            password (str): Cleantext version of the password.

        Returns:
            bool: True if valid.
        """
        with transaction.manager:
            stored_pass_hash = self.users.get(username, None)

        if stored_pass_hash is None:
            return False

        hashed = bcrypt.hashpw(str(password), stored_pass_hash)

        return hashed == stored_pass_hash

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

    @transaction_manager
    def is_empty(self):
        """
        Is the UserHandler database empty?

        Returns:
            bool: True if it is.
        """
        return not list(self.users.keys())
