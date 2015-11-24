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
    """
    This object works as container for metadata and file uploaded thru REST.

    Uploaded files are automatically put into BalancedDiscStorage.

    Attributes:
        cache_dir (str): Directory for BalancedDiscStorage.
        metadata (dict): Dictionary with file's metadata.
        bds_id (str): Hash of the file in BalancedDiscStorage.
        created (float): Timestamp when the object was created.
    """
    def __init__(self, metadata, file_obj, cache_dir=settings.WEB_CACHE):
        """
        Constructor.

        metadata (dict): Dictionary with file's metadata.
        file_obj (file): Reference to opened file object.
        cache_dir (str): Path to the directory for BalancedDiscStorage. Default
            :attr:`.settings.WEB_CACHE`.
        """
        self.cache_dir = cache_dir
        self.metadata = metadata

        # save the file to the BalancedDiscStorage
        self.bds_id = self._bds().add_file(file_obj).hash

        self.created = time.time()

    def _bds(self):
        """
        Dynamically created BalancedDiscStorage object.

        This is used, because I don't want to store the BalancedDiscStorage
        instance in ZODB.

        Returns:
            obj: BalancedDiscStorage instance.
        """
        return BalancedDiscStorage(self.cache_dir)

    def get_file_obj(self):
        """
        Get back reference to opened file object in BalancedDiscStorage.

        Returns:
            file: Opened file object.
        """
        with transaction.manager:
            return open(
                self._bds().file_path_from_hash(self.bds_id),
                "rb"
            )

    def remove_file(self):
        """
        Remove the file from BalancedDiscStorage.

        Warning:
            You should do this before you will garbage collect this object,
            because otherwise you will have a lot of files hanging in your
            BalancedDiscStorage.
        """
        self._bds().delete_by_hash(self.bds_id)

    def __eq__(self, obj):
        return self.bds_id == obj.bds_id

    def __lt__(self, obj):
        return float(self.created).__lt__(obj.created)


class CacheHandler(DatabaseHandler):
    """
    Small queue-like database for the :class:`UploadRequest` objects.

    Attributes:
        cache_key (str): Key used to access the ZEO `path`.
        cache (obj): ZEO tree object.
    """
    def __init__(self, conf_path, project_key):
        """
        Constructor.

        Args:
            conf_path (str): Path to the file with ZEO client configuration.
            project_key (str): Key used to access the ZEO `root`.
        """
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # read the proper index
        self.cache_key = "cache"
        self.cache = self._get_key_or_create(self.cache_key)

    @transaction_manager
    def add(self, metadata, file_obj):
        """
        Create and add new item at the bottom of the queue.

        Args:
            metadata (dict/obj): Metadata structure.
            file_obj (file): Opened file with data.

        Returns:
            obj: :class:`UploadRequest` instance.
        """
        return self.add_upload_request(UploadRequest(metadata, file_obj))

    @transaction_manager
    def add_upload_request(self, upload_request):
        """
        Add new :class:`UploadRequest` at the bottom of the queue.

        Args:
            upload_request (obj): :class:`UploadRequest` instance.

        Returns:
            obj: :class:`UploadRequest` instance.
        """
        error_msg = "`upload_request` parameter have to be instance of "
        error_msg += "UploadRequest!"
        assert isinstance(upload_request, UploadRequest), error_msg

        self.cache[upload_request.bds_id] = upload_request
        return upload_request

    @transaction_manager
    def is_empty(self):
        """
        Is the queue empty?

        Returns:
            bool: True if the queue is empty.
        """
        return len(self.cache.keys()) == 0

    @transaction_manager
    def top(self):
        """
        Get the oldest item from the queue, but leave the item at its position.

        Returns:
            obj: :class:`UploadRequest` instance.
        """
        if not self.cache.keys():
            raise ValueError("There is no cached upload request.")

        oldest = min(self.cache.values(), key=lambda x: x.created)

        return oldest

    @transaction_manager
    def pop(self):
        """
        Remove the oldest item from the queue and return it.

        Returns:
            obj: :class:`UploadRequest` instance.
        """
        if not self.cache.keys():
            return None

        oldest = min(self.cache.values(), key=lambda x: x.created)

        del self.cache[oldest.bds_id]

        return oldest

    @transaction_manager
    def __len__(self):
        return len(self.cache)
