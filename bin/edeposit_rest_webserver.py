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
    from rest.database import UserHandler
except ImportError:
    # from edeposit.amqp.rest import zconf
    from edeposit.amqp.rest import settings
    from edeposit.amqp.rest.database import UserHandler


# Variables ===================================================================
TEMPLATE_PATH = join(
    dirname(__file__), "../src/edeposit/amqp/rest/html_templates"
)
V1_PATH = "/api/v1/"
USERS = UserHandler(
    conf_path=settings.ZEO_CLIENT_CONF_FILE,
    project_key=settings.PROJECT_KEY,
)


# Functions & classes =========================================================
def check_auth(username, password):
    request.environ["username"] = username
    request.environ["password"] = password

    return True  # TODO: remove
    return USERS.is_valid_user(
        username=username,
        password=password
    )


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


@get(join(V1_PATH, "submit"))  # TODO: remove
@post(join(V1_PATH, "submit"))
@auth_basic(check_auth)
@form_to_params
def submit_publication():
    # request.body.readlines()
    return repr(request.environ)


@route("/")
def description_page():
    with open(join(TEMPLATE_PATH, "index.html")) as f:
        content = f.read()

    import dhtmlparser
    from docutils.core import publish_parts

    dom = dhtmlparser.parseString(content)
    for rst in dom.find("rst"):
        rst_content = publish_parts(rst.getContent(), writer_name='html')
        rst_content = rst_content['html_body'].encode("utf-8")
        rst.replaceWith(dhtmlparser.HTMLElement(rst_content))

    return dom.prettify()


# Main program ================================================================
if __name__ == '__main__':
    run(
        server=settings.WEB_SERVER,
        host=settings.WEB_ADDR,
        port=settings.WEB_PORT,
        debug=settings.WEB_DEBUG,
        reloader=settings.WEB_RELOADER,
    )
