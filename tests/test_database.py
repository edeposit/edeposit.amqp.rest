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

from rest.database import UserHandler
from rest.database.user_handler import create_hash


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

    db1.add_user("foo", create_hash("bar"))


def test_multiple_users_creation(user_db):
    for username in permutations("abcd", 4):
        user_db.add_user(username, create_hash(username * 2))


def test_multiple_users_querying(user_db):
    for username in permutations("abcd", 4):
        assert user_db.is_valid_user(username, username * 2)


def test_is_registered(user_db):
    assert user_db.is_registered("foo")
    assert not user_db.is_registered("bar")


def test_is_valid_user_hashed(user_db):
    assert user_db.is_valid_user_hashed("foo", create_hash("bar"))
    assert not user_db.is_valid_user_hashed("foo", "bar")
