#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Structures which may be used to store data in the REST subsystem.
"""
# Imports =====================================================================
from collections import namedtuple


# Functions & classes =========================================================
class SaveLogin(namedtuple("SaveLogin", ["username", "password_hash"])):
    """
    Store new login to the user database.

    Attributes:
        username (str): Name of the user.
        password_hash (str): Bcrypt password hash.
    """


class RemoveLogin(namedtuple("RemoveLogin", ["username"])):
    """
    Remove user from the database.

    Attributes:
        username (str): Name of the user.
    """


class StatusUpdate(namedtuple("StatusUpdate", ["rest_id",
                                               "timestamp",
                                               "message",
                                               "pub_url",
                                               "book_name"])):
    """
    Save new status for the ebook.

    Attributes:
        rest_id (str): String identifying the user's request.
        timestamp (float): Timestamp output from ``time.time()``
        message (str): Content of the message.
        pub_url (str): URL of the book in edeposit.
        book_name (str): Name of the book. If not set (=None), it is used from
            user's metadata.
    """


class CacheTick(namedtuple("CacheTick", [])):
    """
    Tick for the cached uploader, telling it that it is OK to upload one more
    request, if present.

    This structure may also emit the :class:`.AfterDBCleanupRequest`.
    """
