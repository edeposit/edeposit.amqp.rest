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


# Variables ===================================================================
USERNAME = "pepa"
REST_ID = "some id"


# Fixtures ====================================================================
@pytest.fixture
def status_handler():
    return StatusHandler(
        conf_path=tmp_context_name("zeo_client.conf"),
        project_key="key",
    )


# Tests =======================================================================
def test_status_message():
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


def test_status_handler(status_handler):
    with pytest.raises(IndexError):
        status_handler.query_statuses(USERNAME)

    status_handler.register_status_tracking(USERNAME, REST_ID)
    assert status_handler.query_statuses(USERNAME) == {REST_ID: []}