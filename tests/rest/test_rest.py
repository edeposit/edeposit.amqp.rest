#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import json
import urlparse

import pytest
import requests
import dhtmlparser
from requests.auth import HTTPBasicAuth

from rest.database import UserHandler
from rest.database.user_handler import create_hash


# Variables ===================================================================
USERNAME = "user"
PASSWORD = "pass"


# Fixtures ====================================================================
@pytest.fixture
def user_db(client_conf_path):
    return UserHandler(conf_path=client_conf_path)


# Functions ===================================================================
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


def send_request(url, data):
    return requests.post(
        urlparse.urljoin(url, "submit"),
        data={"json_metadata": json.dumps(data)},
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        files={'file': "Whatever"},
        timeout=5,
    )


# Tests =======================================================================
def test_create_user_for_rest(user_db, zeo, client_conf_path):
    user_db.add_user(USERNAME, create_hash(PASSWORD))
    assert user_db.is_valid_user(USERNAME, PASSWORD)


def test_submit_epub_minimal(bottle_server, web_api_url):
    resp = send_request(web_api_url, {
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    assert check_errors(resp)


def test_submit_epub_minimal_numeric(web_api_url):
    resp = send_request(web_api_url, {
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": 1989,  # numeric now!
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    assert check_errors(resp)


def test_submit_epub_minimal_year_fail(web_api_url):
    resp = send_request(web_api_url, {
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "azgabash",  # ordinary string should fail
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    with pytest.raises(ValueError):
        check_errors(resp)


def test_submit_epub_optionals(web_api_url):
    resp = send_request(web_api_url, {
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


def test_submit_epub_optionals_price_error(web_api_url):
    resp = send_request(web_api_url, {
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


def test_submit_epub_optionals_isbn_error(web_api_url):
    resp = send_request(web_api_url, {
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

    resp = send_request(web_api_url, {
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


def test_submit_epub_optionals_isbn_souboru_publikaci_error(web_api_url):
    resp = send_request(web_api_url, {
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


def test_submit_epub_optionals_libraries_error(web_api_url):
    resp = send_request(web_api_url, {
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


def test_submit_epub_optionals_riv_error(web_api_url):
    resp = send_request(web_api_url, {
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


def test_amqp_chain(web_api_url, user_db):
    global USERNAME
    global PASSWORD

    USERNAME = "azgabash"
    PASSWORD = "bar"

    # add new user for following test
    user_db.add_user(USERNAME, create_hash(PASSWORD))

    resp = send_request(web_api_url, {
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    })

    assert check_errors(resp)
