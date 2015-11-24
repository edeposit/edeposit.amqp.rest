#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import random
import string
import os.path

import pytest

from BalancedDiscStorage import BalancedDiscStorage

from rest.database.cache_handler import CacheHandler
from rest.database.cache_handler import UploadRequest


# Variables ===================================================================
# Functions ===================================================================
def random_string(length):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in xrange(length)
    )


# Fixtures ====================================================================
@pytest.fixture
def upload_request(tmpdir_factory):
    file_path = tmpdir_factory.mktemp("tmp").join('%s.pdf' % random_string(5))
    file_path = str(file_path)

    with open(file_path, "w") as f:
        f.write(random_string(20))

    return UploadRequest(
        metadata={"meta": "data"},
        file_obj=open(file_path),
        cache_dir=str(tmpdir_factory.mktemp("bds")),
    )


# Tests =======================================================================
def test_UploadRequest(upload_request):
    with upload_request.get_file_obj() as f:
        assert f.read()

    bds = upload_request._bds()
    data_path = bds.file_path_from_hash(upload_request.bds_id)

    assert os.path.exists(data_path)

    upload_request.remove_file()

    assert not os.path.exists(data_path)


def test_UploadRequest_operators(tmpdir_factory):
    first = upload_request(tmpdir_factory)
    second = upload_request(tmpdir_factory)

    assert first != second
