#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import transaction

from rest.db_handler import ZEOConfWrapper

import environment_generator


# Variables ===================================================================
PROJECT_KEY = "some_key"


# Setup =======================================================================
def setup_module(module):

    environment_generator.generate_environment()


def teardown_module(module):
    environment_generator.cleanup_environment()


# Fixtures ====================================================================
@pytest.fixture
def zeo_wrapper():
    return ZEOConfWrapper(
        conf_path=environment_generator.tmp_context_name("zeo_client.conf"),
        project_key=PROJECT_KEY,
    )


# Tests =======================================================================
def test_storing_and_retreiving():
    first_wrapper = zeo_wrapper()
    second_wrapper = zeo_wrapper()

    with transaction.manager:
        first_wrapper["something"] = "hello"
        assert first_wrapper["something"] == "hello"

    with transaction.manager:
        assert second_wrapper["something"] == "hello"


def test_storing(zeo_wrapper):
    with transaction.manager:
        zeo_wrapper["azgabash"] = "hello"


def test_retreiving(zeo_wrapper):
    with transaction.manager:
        assert zeo_wrapper["azgabash"] == "hello"
