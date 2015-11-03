#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from collections import OrderedDict
from functools import total_ordering

import transaction
from persistent import Persistent
from BTrees.OOBTree import OOSet

from database_handler import DatabaseHandler


# Variables ===================================================================
DAY = 60 * 60 * 24  #: Day in seconds.
MONTH = DAY * 30  #: 30 day month in seconds.
YEAR = DAY * 365  #: Year in seconds.


# Exceptions ==================================================================
class AccessDeniedException(ValueError):
    """
    Exception raised in case that wrong username was given.
    """


# Functions & classes =========================================================
@total_ordering
class StatusMessage(Persistent):
    """
    Message container used to hold `message` with `timestamp` in log stream.

    Attributes:
        message (str): Tracked message.
        timestamp (float): Python timestamp format.
    """
    def __init__(self, message, timestamp):
        self.message = message.strip()
        self.timestamp = float(timestamp)

    def __eq__(self, obj):
        return self.message == obj.message and self.timestamp == obj.timestamp

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __hash__(self):
        return hash((self.timestamp, self.message))

    def __lt__(self, obj):
        return self.timestamp.__lt__(obj.timestamp)


@total_ordering
class StatusInfo(Persistent):
    """
    Object for logging :class:`StatusMessage` objects for given `rest_id`.

    Attributes:
        rest_id (str): REST id for which the messages are tracked.
        pub_url (str): URL of the tracked ebook.
        messages (list): List of :class:`StatusMessage` objects.
        registered_ts (float): Python timestamp format.
    """
    def __init__(self, rest_id, pub_url=None, registered_ts=None):
        """
        Constructor.

        Args:
            rest_id (str): See :attr:`rest_id`.
            pub_url (str, default None): See :attr:`pub_url`.
            registered_ts (float, default None): See :attr:`registered_ts`. If
                not set, current time is used.
        """
        self.rest_id = rest_id
        self.pub_url = pub_url
        self.messages = set()

        if registered_ts:
            self.registered_ts = float(registered_ts)  # for __lt__ operator
        else:
            self.registered_ts = time.time()

    def add_status_message(self, status_message):
        """
        Add `status_message` to internal log of messages.

        Args:
            status_message (obj): :class:`StatusMessage` instance.
        """
        self.messages.add(status_message)

    def add_message(self, message, timestamp):
        """
        Add new :class:`StatusMessage` instance created from `message` and
        `timestamp`.

        Args:
            message (str): Message which will be logged.
            timestamp (float): Timestamp of the message.
        """
        self.add_status_message(
            StatusMessage(message, timestamp)
        )

    def get_messages(self):
        """
        Return sorted list of :attr:`.messages`.

        Returns:
            list: :class`.StatusMessage` instances.
        """
        return sorted(self.messages, key=lambda x: x.timestamp)

    def __eq__(self, obj):
        return self.rest_id == obj.rest_id and self.messages == obj.messages

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __lt__(self, obj):
        return self.registered_ts.__lt__(obj.registered_ts)


class StatusHandler(DatabaseHandler):
    def __init__(self, conf_path, project_key):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        # index for StatusInfo objects
        self.status_db_key = "status"
        self.status_db = self._get_key_or_create(self.status_db_key)

        # index for mapping id->username
        self.status_id_key = "status id->username"
        self.id_to_username = self._get_key_or_create(self.status_id_key)

        # index for mapping username->ids
        self.status_username_key = "status username->ids"
        self.username_to_ids = self._get_key_or_create(
            self.status_username_key
        )

    def log(self, msg): #: TODO: implement
        pass

    def register_status_tracking(self, username, rest_id):
        with transaction.manager:
            # handle id->username mapping
            self.id_to_username[rest_id] = username

            # handle username->ids mapping
            uname_to_ids = self.username_to_ids.get(username, None)
            if uname_to_ids is None:
                uname_to_ids = OOSet()
                self.username_to_ids[username] = uname_to_ids

            # add new rest_id to set
            uname_to_ids.add(rest_id)

            self.status_db[rest_id] = StatusInfo(rest_id=rest_id)

    def save_status_update(self, rest_id, message, timestamp, pub_url=None):
        with transaction.manager:
            status_info_obj = self.status_db.get(rest_id, None)

            # if the `rest_id` is not registered for tracking, just ignore it
            if not status_info_obj:
                return

            if pub_url:
                status_info_obj.pub_url = pub_url

            status_info_obj.add_message(message, timestamp)

    def query_status(self, username, rest_id):
        with transaction.manager:
            status_info_obj = self.status_db.get(rest_id, None)
            db_username = self.id_to_username.get(rest_id, None)

            if not db_username:
                raise IndexError(
                    "User '%s' is not registered to receive status updates for"
                    " '%s'!" % (username, rest_id)
                )

            if username != db_username:
                raise AccessDeniedException(
                    "Item '%s' is not owned by '%s'!" % (rest_id, username)
                )

            if not status_info_obj:
                return []

            return status_info_obj.get_messages()

    def query_statuses(self, username):
        """
        Get informations about all trackings for given `username`.

        Args:
            username (str): Selected username.

        Returns:
            OrderedDict: ``{rest_id: [messages]}``
        """
        with transaction.manager:
            ids = self.username_to_ids.get(username, None)

            if ids is None:
                raise IndexError(
                    "Username '%s' is not registered for tracking!" % username
                )

            # convert list of rest_ids to StatusInfo objects from DB
            status_infos = (
                self.status_db.get(rest_id, None)
                for rest_id in ids
            )

            # filter None elements
            status_infos = (
                status_info
                for status_info in status_infos
                if status_info is not None
            )

            return OrderedDict(
                (si.rest_id, si.get_messages())
                for si in sorted(status_infos, key=lambda x: x.registered_ts)
            )

    def remove_status_info(self, rest_id, username=None):
        with transaction.manager:
            # check privileges of `username` to access `rest_id`
            if username:
                if rest_id not in self.username_to_ids.get(username, []):
                    raise AccessDeniedException(
                        "Can't delete '%s' - invalid owner '%s'." % (
                            rest_id,
                            username,
                        )
                    )

            # remove StatusInfo object
            if rest_id in self.status_db:
                del self.status_db[rest_id]

            # remove from id->username mapping
            stored_username = self.id_to_username.get(rest_id, None)
            if stored_username:
                del self.id_to_username[stored_username]
                username = stored_username

            # remove from username->ids mapping
            if username:
                ids = self.username_to_ids.get(username, None)

                # remove `rest_id` from ids
                if ids is not None and rest_id in ids:
                    self.username_to_ids[username].remove(rest_id)

                # remove empty sets of ids
                if not self.username_to_ids[username]:
                    del self.username_to_ids[username]

    def trigger_garbage_collection(self, interval=YEAR/2):
        with transaction.manager:
            garbage_rest_ids = [
                status_info.rest_id
                for status_info in self.status_db.values()
                if status_info.registered_ts + interval >= time.time()
            ]

        self.log(
            "Garbage collection triggered. Cleaning %d objects: %s" % (
                len(garbage_rest_ids),
                ", ".join(garbage_rest_ids)
            )
        )

        for rest_id in garbage_rest_ids:
            self.remove_status_info(rest_id)
