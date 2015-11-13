#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import sys
import json
import os.path
import argparse
from os.path import join
from os.path import dirname

from bottle import run
from bottle import get
from bottle import post
from bottle import route
from bottle import abort
from bottle import request
from bottle import auth_basic
from bottle import SimpleTemplate

from bottle_rest import form_to_params

# TODO: do requirements
import dhtmlparser
from docutils.core import publish_parts

# TODO: ..
# from edeposit.amqp.models import EpublicationValidator
from models import SchemaError
from models import EpublicationValidator
from models import czech_to_edeposit_dict

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
USER_DB = None


# Functions & classes =========================================================
def check_auth(username, password):
    request.environ["username"] = username
    request.environ["password"] = password

    return True  # TODO: remove
    return USER_DB.is_valid_user(
        username=username,
        password=password
    )


# API definition ==============================================================
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
def submit_publication(json_data):
    metadata = json.loads(json_data)

    filename = metadata.get("nazev_souboru", None)
    if not filename:
        abort(text="Parametr `nazev_souboru` je povinný!")
    del metadata["nazev_souboru"]

    try:
        metadata = EpublicationValidator.validate(metadata)
    except SchemaError as e:
        msg = e.message.replace("Missing keys:", "Chybějící klíče:")
        abort(text=msg)

    edep_metadata = czech_to_edeposit_dict(metadata)

    return edep_metadata


@route("/")
def description_page():
    with open(join(TEMPLATE_PATH, "index.html")) as f:
        content = f.read()

    dom = dhtmlparser.parseString(content)
    for rst in dom.find("rst"):
        rst_content = publish_parts(rst.getContent(), writer_name='html')
        rst_content = rst_content['html_body'].encode("utf-8")
        rst.replaceWith(dhtmlparser.HTMLElement(rst_content))

    return dom.prettify()


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server",
        default=settings.WEB_SERVER,
        help="Type of the server used for threading. Default '%s'." % (
            settings.WEB_SERVER
        )
    )
    parser.add_argument(
        "--host",
        default=settings.WEB_ADDR,
        help="Address to which the bottle should listen. Default '%s'." % (
            settings.WEB_ADDR
        )
    )
    parser.add_argument(
        "--port",
        default=settings.WEB_PORT,
        type=int,
        help="Port on which the server should listen. Default %d." % (
            settings.WEB_PORT
        )
    )
    parser.add_argument(
        "--zeo-client-conf-file",
        default=settings.ZEO_CLIENT_CONF_FILE,
        help="Path to the ZEO configuration file. Default %s." % (
            settings.ZEO_CLIENT_CONF_FILE
        )
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use debug mode. Default False."
    )
    parser.add_argument(
        "--reloader",
        action="store_true",
        help="Use reloader."
    )
    parser.add_argument(
        "--quiet",
        default=False,
        action="store_true",
        help="Be quiet."
    )

    args = parser.parse_args()

    # don't forget to set connection to database
    USER_DB = UserHandler(
        conf_path=args.zeo_client_conf_file,
        project_key=settings.PROJECT_KEY,
    )

    # run the server
    run(
        server=args.server,
        host=args.host,
        port=args.port,
        debug=args.debug or settings.WEB_DEBUG,
        reloader=args.reloader or settings.WEB_RELOADER,
        quiet=args.quiet
    )
else:
    # don't forget to set connection to database
    USER_DB = UserHandler(
        conf_path=settings.ZEO_CLIENT_CONF_FILE,
        project_key=settings.PROJECT_KEY,
    )
