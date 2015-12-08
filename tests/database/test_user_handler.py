#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from itertools import permutations

import pytest

from rest.database import UserHandler
from rest.database.user_handler import create_hash


# Fixtures ====================================================================
@pytest.fixture
def user_db(client_conf_path):
    return UserHandler(conf_path=client_conf_path)


# Tests =======================================================================
def test_user_handling(zeo, client_conf_path):
    db1 = user_db(client_conf_path)

    db1.add_user("foo", create_hash("bar"))

    assert db1.is_valid_user("foo", "bar")
    assert not db1.is_valid_user("foo", "baz")
    assert not db1.is_valid_user("f", "bar")

    db2 = user_db(client_conf_path)

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
        username = "".join(username)
        user_db.add_user(username, create_hash(username * 2))


def test_multiple_users_querying(user_db):
    for username in permutations("abcd", 4):
        username = "".join(username)
        assert user_db.is_valid_user(username, username * 2)


def test_is_registered(user_db):
    assert user_db.is_registered("foo")
    assert not user_db.is_registered("bar")