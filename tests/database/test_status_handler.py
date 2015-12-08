#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import pytest

from zeo_connector_defaults import tmp_context_name

from rest.database import StatusHandler
from rest.database.status_handler import StatusInfo
from rest.database.status_handler import StatusMessage
from rest.database.status_handler import AccessDeniedException


# Variables ===================================================================
USERNAME = "pepa"
REST_ID = "some id"
ALT_REST_ID = "something_else"


# Fixtures ====================================================================
@pytest.fixture
def status_handler():
    return StatusHandler(
        conf_path=tmp_context_name("zeo_client.conf"),
        project_key="key",
    )


# Tests =======================================================================
def test_status_message(zeo):
    s1 = StatusMessage(message="first", timestamp=time.time())
    s2 = StatusMessage(message="second", timestamp=time.time())
    s1_ = StatusMessage(message="first", timestamp=s1.timestamp)

    assert s1 != s2
    assert s1 == s1_

    s_set = set([s1, s2, s1_])

    assert s_set == set([s1, s2])

    assert sorted([s2, s1]) == [s1, s2]


def test_status_info_comparing():
    s1 = StatusInfo(rest_id=REST_ID)
    s2 = StatusInfo(rest_id=REST_ID)

    assert s1 == s2

    sm1 = StatusMessage(message="first", timestamp=time.time())

    s1.add_status_message(sm1)

    assert s1 != s2


def test_status_info_get_messages():
    si = StatusInfo(rest_id=REST_ID)

    params = ("second", time.time())
    si.add_message(*params)

    assert si.get_messages() == [StatusMessage(*params)]


def test_status_info_sorting():
    s1 = StatusInfo(rest_id=REST_ID)
    s2 = StatusInfo(rest_id=REST_ID)

    assert sorted([s2, s1]) == [s1, s2]

    s1 = StatusInfo(rest_id=REST_ID, registered_ts=1)
    s2 = StatusInfo(rest_id=REST_ID)

    assert sorted([s2, s1]) == [s1, s2]


def test_status_handler_register_status_tracking(status_handler):
    with pytest.raises(IndexError):
        status_handler.query_statuses(USERNAME)

    status_handler.register_status_tracking(USERNAME, REST_ID)
    statuses = status_handler.query_statuses(USERNAME)
    assert statuses[0].rest_id == REST_ID
    assert statuses[0].get_messages() == []


def test_status_handler_save_status_update(status_handler):
    m = "Some message."
    t = time.time()
    status_handler.save_status_update(
        rest_id=REST_ID,
        message=m,
        timestamp=t,
        pub_url="http://..",
    )

    query = status_handler.query_statuses(USERNAME)
    assert query[0].rest_id == REST_ID
    assert query[0].get_messages() == [StatusMessage(m, t)]

    # this should do nothing - unregistered rest_id
    status_handler.save_status_update(
        rest_id="azgabash",
        message=m,
        timestamp=t,
        pub_url="http://..",
    )

    query = status_handler.query_status(REST_ID, USERNAME)
    assert query == [StatusMessage(m, t)]

    # and now without username
    query = status_handler.query_status(REST_ID)
    assert query == [StatusMessage(m, t)]


def test_status_handler_query_status_exceptions(status_handler):
    with pytest.raises(IndexError):
        status_handler.query_status("azgabash", USERNAME)

    status_handler.register_status_tracking(USERNAME, ALT_REST_ID)
    with pytest.raises(AccessDeniedException):
        status_handler.query_status(REST_ID, "azgabash")


def test_status_handler_remove_status_info(status_handler):
    statuses = status_handler.query_statuses(USERNAME)
    assert ALT_REST_ID in [status.rest_id for status in statuses]

    with pytest.raises(AccessDeniedException):
        status_handler.remove_status_info(
            username="tona hluchonemec",
            rest_id=ALT_REST_ID,
        )

    status_handler.remove_status_info(rest_id=ALT_REST_ID)

    assert ALT_REST_ID not in status_handler.query_statuses(USERNAME)


def test_remove_user(status_handler):
    status_handler.register_status_tracking(USERNAME, ALT_REST_ID)

    assert status_handler.query_statuses(USERNAME)

    status_handler.remove_user(USERNAME)

    with pytest.raises(IndexError):
        status_handler.query_statuses(REST_ID)


def test_status_handler_trigger_garbage_collection(status_handler):
    status_handler.trigger_garbage_collection(interval=0)

    with pytest.raises(IndexError):
        status_handler.query_statuses(USERNAME)
