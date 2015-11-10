#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import time
import json
import random
import urlparse
import threading
import subprocess

import pytest
import requests
from requests.auth import HTTPBasicAuth
from zeo_connector_defaults import CLIENT_CONF_PATH


# Variables ===================================================================
PORT = random.randint(20000, 60000)
URL = "http://127.0.0.1:%d/api/v1/" % PORT
SERV = None


# Fixtures ====================================================================
@pytest.fixture(scope="module", autouse=True)
def bottle_server(request, zeo):
    # run the bottle REST server
    def run_bottle():
        command_path = os.path.join(
            os.path.dirname(__file__),
            "../../bin/edeposit_rest_webserver.py"
        )

        assert os.path.exists(command_path)

        global SERV
        SERV = subprocess.Popen([
            command_path,
            "--zeo-client-conf-file", CLIENT_CONF_PATH,
            "--port", str(PORT),
            "--host", "127.0.0.1",
            "--server", "paste",
            "--debug",
            "--quiet",
        ])

    serv = threading.Thread(target=run_bottle)
    serv.setDaemon(True)
    serv.start()

    time.sleep(1)  # TODO: replace with circuit breaked http ping

    def shutdown_server():
        SERV.terminate()

    request.addfinalizer(shutdown_server)


# Tests =======================================================================
def test_send(bottle_server):
    data = {
        "title": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
    }

    resp = requests.post(
        urlparse.urljoin(URL, "submit"),
        data={"json_data": json.dumps(data)},
        auth=HTTPBasicAuth('user', 'pass'),
    )
    print resp.text
