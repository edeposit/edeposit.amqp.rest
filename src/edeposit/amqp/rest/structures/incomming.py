#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Variables ===================================================================
# Functions & classes =========================================================
class SaveLogin(namedtuple("SaveLogin", ["username", "password_hash"])):
    """
    """


class RemoveLogin(namedtuple("RemoveLogin", ["username"])):
    """
    """


class StatusUpdate(namedtuple("StatusUpdate", ["rest_id",
                                               "timestamp",
                                               "message",
                                               "pub_url",
                                               "book_name"])):
    """
    """
