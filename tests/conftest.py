#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from zeo_connector_defaults import generate_environment
from zeo_connector_defaults import cleanup_environment


# Setup =======================================================================
@pytest.fixture(scope="session", autouse=True)
def zeo(request):
    generate_environment()
    request.addfinalizer(cleanup_environment)
