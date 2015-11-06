#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import os.path
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/edeposit/amqp"))
try:
    from rest import settings
except ImportError:
    from edeposit.amqp.rest import settings


# Variables ===================================================================
assert settings.ZEO_SERVER_CONF_FILE, settings._format_error(
    "ZEO_SERVER_CONF_FILE",
    settings.ZEO_SERVER_CONF_FILE
)


# Main program ================================================================
if __name__ == '__main__':
    subprocess.check_call(["runzeo", "-C", settings.ZEO_SERVER_CONF_FILE])
