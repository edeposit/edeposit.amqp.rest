#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from functools import total_ordering

import transaction
from persistent import Persistent

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler

from BalancedDiscStorage import BalancedDiscStorage

from .. import settings


# Functions & classes =========================================================
@total_ordering
class UploadRequest(Persistent):
    def __init__(self, metadata, file_obj, cache_dir=settings.WEB_CACHE):
        self.cache_dir = cache_dir
        self.metadata = metadata

        # save the file to the BalancedDiscStorage
        self.bds_id = self._bds().add_file(file_obj).hash

        self.created = time.time()

    def _bds(self):
        return BalancedDiscStorage(self.cache_dir)

    def get_file_obj(self):
        with transaction.manager:
            return open(
                self._bds().file_path_from_hash(self.bds_id),
                "rb"
            )

    def remove_file(self):
        self._bds().delete_by_hash(self.bds_id)

    def __eq__(self, obj):
        return self.bds_id == obj.bds_id

    def __lt__(self, obj):
        return float(self.created).__lt__(obj.created)


class CacheHandler(DatabaseHandler):
    """
    """
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.cache_key = "cache"
        self.cache = self._get_key_or_create(self.cache_key)

    @transaction_manager
    def add_upload_request(self, metadata, bds_id):
        self.cache[bds_id] = UploadRequest(metadata, bds_id)

    @transaction_manager
    def has_upload_request(self):
        return len(self.cache.keys()) > 0

    @transaction_manager
    def get_upload_request(self):
        if not self.cache.keys():
            raise ValueError("There is no cached upload request.")

        oldest = min(self.cache.values(), key=lambda x: x.created)

        return oldest

    def pop_upload_requst(self):
        if not self.cache.keys():
            return None

        oldest = min(self.cache.values(), key=lambda x: x.created)

        del self.cache[oldest.bds_id]

        return oldest
