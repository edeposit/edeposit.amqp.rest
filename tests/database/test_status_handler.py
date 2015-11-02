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
from rest.database.status_handler import SatusMessage


# Fixtures ====================================================================
@pytest.fixture
def status_handler():
    return StatusHandler(
        conf_path=tmp_context_name("zeo_client.conf"),
        project_key="key",
    )


# Tests =======================================================================
def test_status_message():
    s1 = SatusMessage(message="first", timestamp=time.time())
    s2 = SatusMessage(message="second", timestamp=time.time())
    s1_ = SatusMessage(message="first", timestamp=s1.timestamp)

    assert s1 != s2
    assert s1 == s1_

    s_set = set([s1, s2, s1_])

    assert s_set == set([s1, s2])

    assert sorted([s2, s1]) == [s1, s2]


def test_status_info():
    rest_id = "some id"

    si = StatusInfo(rest_id=rest_id)


# def test_something(status_handler):
#     pass
