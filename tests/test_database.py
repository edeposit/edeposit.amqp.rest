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
def test_db(db_obj):
    pass