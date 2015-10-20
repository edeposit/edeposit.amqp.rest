#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

import transaction

from rest.db_handler import ZEOWrapper
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
def zeo_conf_wrapper():
    return ZEOConfWrapper(
        conf_path=environment_generator.tmp_context_name("zeo_client.conf"),
        project_key=PROJECT_KEY,
    )


@pytest.fixture
def zeo_wrapper():
    return ZEOWrapper(
        server="localhost",
        port=60985,
        project_key=PROJECT_KEY,
    )


# Tests =======================================================================
def test_zeo_conf_wrapper_storing_and_retreiving():
    first_wrapper = zeo_conf_wrapper()
    second_wrapper = zeo_conf_wrapper()

    with transaction.manager:
        first_wrapper["something"] = "hello"
        assert first_wrapper["something"] == "hello"

    with transaction.manager:
        assert second_wrapper["something"] == "hello"


def test_zeo_conf_wrapper_storing(zeo_conf_wrapper):
    with transaction.manager:
        zeo_conf_wrapper["azgabash"] = "hello"


def test_zeo_conf_wrapper_retreiving(zeo_conf_wrapper):
    with transaction.manager:
        assert zeo_conf_wrapper["azgabash"] == "hello"


def test_zeo_wrapper_retreiving(zeo_wrapper):
    with transaction.manager:
        assert zeo_wrapper["azgabash"] == "hello"


def test_zeo_wrapper_storing(zeo_wrapper):
    with transaction.manager:
        zeo_wrapper["zeo"] = "hello ZEO"


def test_zeo_wrapper_retreiving_again(zeo_wrapper):
    with transaction.manager:
        assert zeo_wrapper["zeo"] == "hello ZEO"