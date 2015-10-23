#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from itertools import permutations

import pytest

from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment
from zeo_connector_defaults import tmp_context_name

from rest import UserHandler
from rest.database import create_hash


# Variables ===================================================================
# Setup =======================================================================
def setup_module(module):
    generate_environment()


def teardown_module(module):
    cleanup_environment()


# Fixtures ====================================================================
@pytest.fixture
def user_db():
    return UserHandler(
        conf_path=tmp_context_name("zeo_client.conf"),
        project_key="key",
    )


# Tests =======================================================================
def test_user_handling():
    db1 = user_db()

    db1.add_user("foo", create_hash("bar"))

    assert db1.is_valid_user("foo", "bar")
    assert not db1.is_valid_user("foo", "baz")
    assert not db1.is_valid_user("f", "bar")

    db2 = user_db()

    assert db2.is_valid_user("foo", "bar")
    assert not db2.is_valid_user("foo", "baz")
    assert not db2.is_valid_user("f", "bar")

    db2.remove_user("foo")

    assert not db1.is_valid_user("foo", "bar")
    assert not db2.is_valid_user("foo", "bar")

    with pytest.raises(AssertionError):
        assert db2.is_valid_user("foo", "bar")


def test_multiple_users_creation():
    db = user_db()

    for username in permutations("abcd", 4):
        db.add_user(username, create_hash(username * 2))


def test_multiple_users_querying():
    db = user_db()

    for username in permutations("abcd", 4):
        assert db.is_valid_user(username, username * 2)
