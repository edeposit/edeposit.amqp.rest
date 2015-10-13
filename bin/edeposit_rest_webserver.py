#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import sys
import os.path
from os.path import join
from os.path import dirname

from bottle import run
from bottle import route
from bottle import SimpleTemplate

sys.path.insert(0, join(dirname(__file__), "../src/edeposit/amqp"))

try:
    # from rest import zconf
    from rest import settings
except ImportError:
    # from edeposit.amqp.rest import zconf
    from edeposit.amqp.rest import settings


# Variables ===================================================================
TEMPLATE_PATH = join(dirname(__file__), "../src/edeposit/amqp/rest/templates")


# Functions & classes =========================================================
@route("/")
def index():
    with open(join(TEMPLATE_PATH, "index.html")) as f:
        return f.read()


# Main program ================================================================
if __name__ == '__main__':
    run(
        server=settings.WEB_SERVER,
        host=settings.WEB_ADDR,
        port=settings.WEB_PORT,
        debug=settings.WEB_DEBUG,
        reloader=settings.WEB_RELOADER,
    )
