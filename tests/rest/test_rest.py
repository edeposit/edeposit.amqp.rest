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
import dhtmlparser
from requests.auth import HTTPBasicAuth
from zeo_connector_defaults import CLIENT_CONF_PATH


# Variables ===================================================================
PORT = random.randint(20000, 60000)
URL = "http://127.0.0.1:%d" % PORT
API_URL = URL + "/api/v1/"
SERV = None


# Functions ===================================================================
def circuit_breaker_http_retry():
    for i in range(10):
        try:
            return requests.get(URL).raise_for_status()
        except Exception:
            time.sleep(1)

    raise IOError("Couldn't connect to thread with HTTP server. Aborting.")


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

    circuit_breaker_http_retry()

    def shutdown_server():
        SERV.terminate()

    request.addfinalizer(shutdown_server)


# Tests =======================================================================
def check_errors(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        dom = dhtmlparser.parseString(response.text.encode("utf-8"))
        pre = dom.find("pre")

        if not pre:
            raise ValueError(e.message)

        pre_el = pre[0] if len(pre) == 1 else pre[1]

        error_msg = pre_el.getContent()
        error_msg = error_msg.replace("&#039;", "'")
        error_msg = error_msg.replace("&quote;", '"')
        error_msg = error_msg.replace("&quot;", '"')
        raise ValueError(error_msg)

    return response.text


def send_request(data):
    return requests.post(
        urlparse.urljoin(API_URL, "submit"),
        data={"json_metadata": json.dumps(data)},
        auth=HTTPBasicAuth('user', 'pass'),
    )


def test_submit_epub_minimal(bottle_server):
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    assert check_errors(resp)


def test_submit_epub_minimal_numeric():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,  # numeric now!
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    assert check_errors(resp)


def test_submit_epub_minimal_year_fail():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "azgabash",  # ordinary string should fail
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "cena": "123",
        "isbn": "80-7169-860-1",
        "isbn_souboru_publikaci": "80-7169-860-1",
        "zpristupneni": ["moravska-zemska-knihovna-v-brne"],
        "riv": 10,
    })

    assert check_errors(resp)


def test_submit_epub_optionals_price_error():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "cena": "123 kč",
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals_isbn_error():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "isbn": "80-7169-860-2",  # wrong checksum
    })

    with pytest.raises(ValueError):
        check_errors(resp)

    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "isbn": "",
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals_isbn_souboru_publikaci_error():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "isbn_souboru_publikaci": "80-7169-860-2",  # wrong checksum
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals_libraries_error():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "zpristupneni": ["nejaka vymyslena"],
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals_riv_error():
    resp = send_request({
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
        "riv": 155,
    })

    with pytest.raises(ValueError):
        check_errors(resp)
