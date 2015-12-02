#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import base64
import tempfile

from structures import CacheTick
from structures import SaveLogin
from structures import RemoveLogin
from structures import StatusUpdate
from structures import UploadRequest

import settings
from database import UserHandler as _UserHandler
from database import CacheHandler as _CacheHandler
from database import StatusHandler as _StatusHandler


# Functions & classes =========================================================
def _instanceof(instance, cls):
    """
    Check type of `instance` by matching ``.__name__`` with `cls.__name__`.
    """
    return type(instance).__name__ == cls.__name__


# Main function ===============================================================
def reactToAMQPMessage(message, send_back):
    """
    React to given (AMQP) message. `message` is expected to be
    :py:func:`collections.namedtuple` structure from :mod:`.structures` filled
    with all necessary data.

    Args:
        message (object): One of the request objects defined in
                          :mod:`.structures`.
        send_back (fn reference): Reference to function for responding. This is
                  useful for progress monitoring for example. Function takes
                  one parameter, which may be response structure/namedtuple, or
                  string or whatever would be normally returned.

    Returns:
        object: Response class from :mod:`structures`.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    user_db = _UserHandler(
        conf_path=settings.ZEO_CLIENT_CONF_FILE,
        project_key=settings.PROJECT_KEY,
    )
    status_db = _StatusHandler(
        conf_path=settings.ZEO_CLIENT_CONF_FILE,
        project_key=settings.PROJECT_KEY,
    )
    cache_db = _CacheHandler(
        conf_path=settings.ZEO_CLIENT_CONF_FILE,
        project_key=settings.PROJECT_KEY,
    )

    if _instanceof(message, SaveLogin):
        return user_db.add_user(
            username=message.username,
            pw_hash=message.password_hash,
        )
    elif _instanceof(message, RemoveLogin):
        return user_db.remove_user(
            username=message.username
        )
    elif _instanceof(message, CacheTick):
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

        return req
    elif _instanceof(message, StatusUpdate):
        status_db.save_status_update(
            rest_id=message.rest_id,
            message=message.message,
            timestamp=message.timestamp,
            book_name=message.book_name,
            pub_url=message.pub_url,
        )

    raise ValueError("'%s' is unknown type of request!" % str(type(message)))
