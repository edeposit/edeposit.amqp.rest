#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Structures which are sent back to edeposit.
"""
# Imports =====================================================================
from collections import namedtuple


# Functions & classes =========================================================
class UploadRequest(namedtuple("UploadRequest", ["username",
                                                 "rest_id",
                                                 "b64_data",
                                                 "metadata"])):
    """
    User's upload request with following data:

    Attributes:
        username (str): User's handle in the REST system. See
            :class:`.SaveLogin` and :class:`.RemoveLogin`.
        rest_id (str): Unique identificator of the request.
        b64_data (str): Content of the file packed as base64 data.
        metadata (dict): Dictionary with metadata.
    """


class AfterDBCleanupRequest(namedtuple("AfterDBCleanupRequest", [])):
    """
    Request refill of the user-related informations after the database was
    cleaned.
    """
