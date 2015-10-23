#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment
from zeo_connector_defaults import tmp_context_name

from rest import DatabaseHandler
from rest.database import create_hash


# Variables ===================================================================
# Setup =======================================================================
def setup_module(module):
    generate_environment()


def teardown_module(module):
    cleanup_environment()


# Fixtures ====================================================================
@pytest.fixture
def db_obj():
    return DatabaseHandler(
        conf_path=tmp_context_name("zeo_client.conf"),
        project_key="key",
    )


# Tests =======================================================================
def test_user_handling():
    db1 = db_obj()

    db1.add_user("foo", create_hash("bar"))

    assert db1.is_valid_user("foo", "bar")
    assert not db1.is_valid_user("foo", "baz")
    assert not db1.is_valid_user("f", "bar")

    db2 = db_obj()

    assert db2.is_valid_user("foo", "bar")
    assert not db2.is_valid_user("foo", "baz")
    assert not db2.is_valid_user("f", "bar")

    db2.remove_user("foo")

    assert not db1.is_valid_user("foo", "bar")
    assert not db2.is_valid_user("foo", "bar")

    with pytest.raises(AssertionError):
        assert db2.is_valid_user("foo", "bar")


def test_multiple_users_handling():
    for i in 
