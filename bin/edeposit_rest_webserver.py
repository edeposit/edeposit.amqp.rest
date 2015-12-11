#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import sys
import json
import time
import uuid
import traceback
from os.path import join
from os.path import dirname

from bottle import run
from bottle import get
from bottle import post
from bottle import route
from bottle import abort
from bottle import request
from bottle import auth_basic
from bottle import HTTPResponse

from bottle_rest import form_to_params

import dhtmlparser
from docutils.core import publish_parts

try:
    from models import SchemaError
    from models import EpublicationValidator
    from models import czech_to_edeposit_dict
    from models.riv import RIV_CATEGORIES
    from models.libraries import LIBRARY_MAP
    from models.libraries import DEFAULT_LIBRARY
except ImportError:
    from edeposit.amqp.models import SchemaError
    from edeposit.amqp.models import EpublicationValidator
    from edeposit.amqp.models import czech_to_edeposit_dict
    from edeposit.amqp.models.riv import RIV_CATEGORIES
    from edeposit.amqp.models.libraries import LIBRARY_MAP
    from edeposit.amqp.models.libraries import DEFAULT_LIBRARY

sys.path.insert(0, join(dirname(__file__), "../src/edeposit/amqp"))

try:
    from rest import settings
    from rest.database import UserHandler
    from rest.database import CacheHandler
    from rest.database import StatusHandler
except ImportError:
    from edeposit.amqp.rest import settings
    from edeposit.amqp.rest.database import UserHandler
    from edeposit.amqp.rest.database import CacheHandler
    from edeposit.amqp.rest.database import StatusHandler


# Variables ===================================================================
TEMPLATE_PATH = join(
    dirname(__file__), "../src/edeposit/amqp/rest/html_templates"
)
V1_PATH = "/api/v1/"  # TODO: api_v1
USER_DB = None


# Functions & classes =========================================================
def check_auth(username, password):
    request.environ["username"] = username
    request.environ["password"] = password

    # for some strange reason, this has to be initialized in the function, not
    # at the beginning of the file
    global USER_DB
    if not USER_DB:
        USER_DB = UserHandler(conf_path=settings.ZEO_CLIENT_CONF_FILE)

    return USER_DB.is_valid_user(
        username=username,
        password=password
    )


def process_metadata(json_metadata):
    metadata = json.loads(json_metadata)

    # make sure, that `nazev_souboru` is present in input metadata
    filename = metadata.get("nazev_souboru", None)
    if not filename:
        abort(text="Parametr `nazev_souboru` je povinný!")
    del metadata["nazev_souboru"]

    # validate structure of metadata and map errors to abort() messages
    try:
        metadata = EpublicationValidator.validate(metadata)
    except SchemaError as e:
        msg = str(e.message).replace("Missing keys:", "Chybějící klíče:")
        abort(text=msg)

    # add DEFAULT_LIBRARY to metadata - it is always present
    libraries = metadata.get("libraries_that_can_access", [])
    libraries.append(DEFAULT_LIBRARY)
    metadata["libraries_that_can_access"] = libraries

    # convert input metadata to data for edeposit
    return czech_to_edeposit_dict(metadata)


def status_info_to_dict(si):
    def msg_to_dict(msg):
        return {
            "message": msg.message,
            "timestamp": msg.timestamp,
        }

    return {
        "pub_url": si.pub_url,
        "book_name": si.book_name,
        "messages": [
            msg_to_dict(msg)
            for msg in si.get_messages()
        ]
    }


def handle_errors(fn):
    def handle_errors_decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = {"error": e.message}
            if settings.WEB_DEBUG:
                msg["traceback"] = traceback.format_exc().strip()

            raise HTTPResponse(json.dumps(msg), 400)

    return handle_errors_decorator


# API definition ==============================================================
@get(join(V1_PATH, "track/<rest_id>"))
@auth_basic(check_auth)
@handle_errors
def track_publication(rest_id=None):
    if not rest_id:
        return track_publications()

    status_db = StatusHandler()
    return status_info_to_dict(
        status_db.query_status(
            rest_id=rest_id,
            username=request.environ["username"],
        )
    )


@get(join(V1_PATH, "track"))
@auth_basic(check_auth)
@handle_errors
def track_publications():
    status_db = StatusHandler()

    return {
        status.rest_id: status_info_to_dict(status)
        for status in status_db.query_statuses(request.environ["username"])
    }


@get(join(V1_PATH, "submit"))  # TODO: remove
@post(join(V1_PATH, "submit"))
@auth_basic(check_auth)
@form_to_params
@handle_errors
def submit_publication(json_metadata):
    username = request.environ["username"]
    metadata = process_metadata(json_metadata)

    # make sure that user is sending the file with the metadata
    if not request.files:
        abort(text="Tělo requestu musí obsahovat ohlašovaný soubor!")

    # get handler to upload object
    file_key = request.files.keys()[0]
    upload_file = request.files[file_key].file

    # generate the ID for the REST request
    rest_id = str(uuid.uuid4())
    metadata["rest_id"] = rest_id

    # put it into the cache database
    cache_db = CacheHandler()
    cache_db.add(
        username=username,
        rest_id=rest_id,
        metadata=metadata,
        file_obj=upload_file,
    )

    # put the tracking request to the StatusHandler
    status_db = StatusHandler()
    status_db.register_status_tracking(
        username=username,
        rest_id=rest_id
    )
    status_db.save_status_update(
        rest_id=rest_id,
        book_name=metadata["title"],
        timestamp=time.time(),
        message="Ohlaseno pres REST.",
    )

    return rest_id


@get(join(V1_PATH, "structures", "riv"))
def riv_structure():
    return dict(RIV_CATEGORIES)


@get(join(V1_PATH, "structures", "library_map"))
def library_structure():
    return LIBRARY_MAP


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
    # run the server
    run(
        server=settings.WEB_SERVER,
        host=settings.WEB_ADDR,
        port=settings.WEB_PORT,
        debug=settings.WEB_DEBUG,
        reloader=settings.WEB_RELOADER,
        quiet=settings.WEB_BE_QUIET,
    )
