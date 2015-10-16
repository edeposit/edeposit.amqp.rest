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
from bottle import get
from bottle import post
from bottle import route
from bottle import request
from bottle import auth_basic
from bottle import SimpleTemplate

from bottle_rest import form_to_params

sys.path.insert(0, join(dirname(__file__), "../src/edeposit/amqp"))

try:
    # from rest import zconf
    from rest import settings
except ImportError:
    # from edeposit.amqp.rest import zconf
    from edeposit.amqp.rest import settings


# Variables ===================================================================
TEMPLATE_PATH = join(
    dirname(__file__), "../src/edeposit/amqp/rest/html_templates"
)
V1_PATH = "/api/v1/"


# Functions & classes =========================================================
def check_auth(username, password):
    return True


# API definition =========================================================
@route(join(V1_PATH, "track/<uid>"))
@auth_basic(check_auth)
def track_publication(uid=None):
    if not uid:
        return track_publications()


@route(join(V1_PATH, "track"))
@auth_basic(check_auth)
def track_publications():
    pass


@post(join(V1_PATH, "submit"))
@form_to_params
@auth_basic(check_auth)
def submit_publication():
    request.body.readlines()


@route("/")
def description_page():
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
