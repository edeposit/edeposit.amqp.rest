#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from contextlib import contextmanager

import pytest


# Variables ===================================================================
_TESTVAR = None


# Functions ===================================================================
@contextmanager
def manager():
    global _TESTVAR
    _TESTVAR = 1

    yield "something"

    # this shouldn't happen if there was an exception during yield
    _TESTVAR = 2


# Tests =======================================================================
def test_manager():
    with pytest.raises(Exception):
        with manager() as f:
            assert f == "something"
            assert _TESTVAR == 1

            raise ValueError("Something")

    assert _TESTVAR == 1
