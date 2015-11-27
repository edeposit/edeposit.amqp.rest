#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import base64
import os.path
import tempfile

path = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(path, "../src/edeposit/amqp"))

try:
    from rest import settings
    from rest.database import CacheHandler
    from rest.structures import UploadRequest
except ImportError:
    from edeposit.amqp.rest import settings
    from edeposit.amqp.rest.database import CacheHandler
    from edeposit.amqp.rest.structures import UploadRequest


# Variables ===================================================================



# Functions & classes =========================================================
def send(req):
    pass


def process_request():
    cache_db = CacheHandler()

    if cache_db.is_empty():
        return

    with cache_db.pop_manager() as cached_request:
        fp = cached_request.get_file_obj()

        with tempfile.TemporaryFile() as f:
            base64.encode(fp, f)

            f.seek(0)
            req = UploadRequest(
                username=cached_request.username,
                rest_id=cached_request.rest_id,
                b64_data=f.read(),
                metadata=cached_request.metadata,
            )

        fp.close()
        send(req)


# Main program ================================================================
if __name__ == '__main__':
    process_request()
