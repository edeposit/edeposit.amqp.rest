#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __future__ import unicode_literals

import json
import urlparse

import os
import time
import pytest
import os.path
import requests
import dhtmlparser
from requests.auth import HTTPBasicAuth

import rest
from rest.database import UserHandler
from rest.database import CacheHandler
from rest.database import StatusHandler
from rest.database.user_handler import create_hash


# Variables ===================================================================
USERNAME = "user"
PASSWORD = "pass"


# Fixtures ====================================================================
@pytest.fixture
def user_db(client_conf_path):
    return UserHandler(conf_path=client_conf_path)


@pytest.fixture
def cache_db(client_conf_path):
    return CacheHandler(conf_path=client_conf_path)


@pytest.fixture
def status_db(client_conf_path):
    return StatusHandler(conf_path=client_conf_path)



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


def test_amqp_chain(web_api_url, user_db, cache_db, status_db, alt_conf_path):
    global USERNAME
    global PASSWORD

    USERNAME = "azgabash"
    PASSWORD = "bar"

    # set alternative path for settings file
    os.environ["SETTINGS_PATH"] = alt_conf_path

    # this has to be here, because of env for settings
    reload(rest.settings)

    # add new user for following test
    rest.reactToAMQPMessage(
        rest.SaveLogin(
            username=USERNAME,
            password_hash=create_hash(PASSWORD),
        ),
        lambda x: x
    )

    # clean up cache_db from previous requests
    while not cache_db.is_empty():
        el = cache_db.pop()
        el.remove_file()

    assert cache_db.is_empty()

    # make sure that also status_db is empty
    with pytest.raises(IndexError):
        status_db.query_statuses(USERNAME)

    # send new request
    dataset = {
        "nazev": "Název",
        "poradi_vydani": "3",
        "misto_vydani": "Praha",
        "rok_vydani": "1989",
        "zpracovatel_zaznamu": "/me",
        "nazev_souboru": "story_of_mighty_azgabash.pdf",
    }
    resp = send_request(web_api_url, dataset)

    assert check_errors(resp)

    # check the state of the database
    assert not cache_db.is_empty()
    status_info = status_db.query_statuses(USERNAME)[0]
    assert status_info.book_name == dataset["nazev"]
    assert status_info.pub_url is None
    assert len(status_info.get_messages()) == 1

    # try to save status update message
    update_msg = rest.StatusUpdate(
        rest_id=status_info.rest_id,
        timestamp=time.time(),
        message="Update message.",
        pub_url="http://somepuburl",
        book_name=None,
    )
    rest.reactToAMQPMessage(update_msg, lambda x: x)

    # test that new statusinfo update was successfully saved to DB
    assert not cache_db.is_empty()
    status_info = status_db.query_statuses(USERNAME)[0]
    assert status_info.book_name == dataset["nazev"]
    assert status_info.pub_url == update_msg.pub_url
    assert len(status_info.get_messages()) == 2
    assert status_info.get_messages()[1].message == update_msg.message
    assert status_info.get_messages()[1].timestamp == update_msg.timestamp

    file_path = cache_db.top().get_file_path()
    assert os.path.exists(file_path)

    # pick item from the cache
    response = rest.reactToAMQPMessage(rest.CacheTick(), lambda x: x)

    # assert that only the cache was changed
    assert cache_db.is_empty()
    status_info = status_db.query_statuses(USERNAME)[0]
    assert status_info.book_name == dataset["nazev"]
    assert status_info.pub_url == update_msg.pub_url
    assert len(status_info.get_messages()) == 2
    assert status_info.get_messages()[1].message == update_msg.message
    assert status_info.get_messages()[1].timestamp == update_msg.timestamp

    assert response.username == USERNAME
    assert response.rest_id == status_info.rest_id
    assert response.b64_data
    assert response.metadata["title"] == dataset["nazev"]

    # remove user from the user_db
    rest.reactToAMQPMessage(rest.RemoveLogin(USERNAME), lambda x: x)

    # make sure that also status_db and cache_db is empty
    assert cache_db.is_empty()
    with pytest.raises(IndexError):
        status_db.query_statuses(USERNAME)
    assert not os.path.exists(file_path)
