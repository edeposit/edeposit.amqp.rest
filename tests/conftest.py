#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import os
import json
import time
import random
import tempfile
import subprocess
import multiprocessing

import pytest
import requests

from zeo_connector_defaults import tmp_context_name
from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment


# Variables ===================================================================
PORT = random.randint(20000, 60000)
URL = "http://127.0.0.1:%d" % PORT
API_URL = URL + "/api/v1/"
_SERVER_HANDLER = None


# Functions ===================================================================
def circuit_breaker_http_retry(max_retry=10):
    for i in range(max_retry):
        try:
            print "Connecting to server .. %d/%d" % (i + 1, max_retry)
            return requests.get(URL).raise_for_status()
        except Exception:
            time.sleep(1)

    raise IOError("Couldn't connect to thread with HTTP server. Aborting.")


def _create_alt_settings(client_path, server_path):
    alt_settings = {
        "ZEO_CLIENT_CONF_FILE": client_path,
        "ZEO_SERVER_CONF_FILE": server_path,

        "WEB_ADDR": "127.0.0.1",
        "WEB_PORT": web_port(),
        "WEB_SERVER": "paste",
        "WEB_DEBUG": True,
        "WEB_RELOADER": True,
        "WEB_BE_QUIET": True,
        "WEB_CACHE": "/tmp",
    }

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(json.dumps(alt_settings))
        return f.name


# Setup =======================================================================
@pytest.fixture(scope="session", autouse=True)
def zeo(request):
    generate_environment()
    request.addfinalizer(cleanup_environment)


# Fixtures ====================================================================
@pytest.fixture(scope="session", autouse=True)
def web_port():
    return PORT


@pytest.fixture(scope="session", autouse=True)
def web_api_url():
    return API_URL


@pytest.fixture(scope="session", autouse=True)
def client_conf_path(zeo):
    return tmp_context_name("zeo_client.conf")


@pytest.fixture(scope="session", autouse=True)
def server_conf_path(zeo):
    return tmp_context_name("zeo.conf")


@pytest.fixture(scope="session", autouse=True)
def alt_conf_path(client_conf_path, server_conf_path):
    return _create_alt_settings(
        client_path=client_conf_path,
        server_path=server_conf_path,
    )


@pytest.fixture(scope="session", autouse=True)
def bottle_server(request, zeo, alt_conf_path):
    os.environ["SETTINGS_PATH"] = alt_conf_path

    # run the bottle REST server
    class BottleProcess(multiprocessing.Process):
        def __init__(self, alt_conf_path):
            multiprocessing.Process.__init__(self)
            self._server_handler = None
            self.alt_conf_path = alt_conf_path

            self.exit = multiprocessing.Event()

        def run(self):
            command_path = os.path.join(
                os.path.dirname(__file__),
                "../bin/edeposit_rest_webserver.py"
            )

            assert os.path.exists(command_path)

            # replace settings with mocked file
            os.environ["SETTINGS_PATH"] = alt_conf_path

            self._server_handler = subprocess.Popen(
                command_path,
                env=os.environ,
            )

        def shutdown(self):
            if self._server_handler:
                self._server_handler.terminate()

            self.exit.set()

    serv = BottleProcess(alt_conf_path)
    serv.start()

    # add finalizer which shutdowns the server and remove temporary file
    def shutdown_server():
        serv.shutdown()
        os.unlink(alt_conf_path)

    request.addfinalizer(shutdown_server)

    # wait until the connection with server is created
    circuit_breaker_http_retry()
