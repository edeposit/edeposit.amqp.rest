#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Variables ===================================================================
# Functions & classes =========================================================
class UploadRequest(namedtuple("UploadRequest", ["username",
                                                 "rest_id",
                                                 "b64_data",
                                                 "metadata"])):
    """
    """


class AfterDBCleanupRequest(namedtuple("AfterDBCleanupRequest", [])):
    """
    Request refill of the user-related informations after the database was
    cleaned.
    """
