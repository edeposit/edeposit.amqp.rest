#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import transaction
from persistent import Persistent
from BTrees.OOBTree import OOSet

from database_handler import DatabaseHandler


# Variables ===================================================================
DAY = 60 * 60 * 24
MONTH = DAY * 30
YEAR = DAY * 365


# Exceptions ==================================================================
class AccessDeniedException(ValueError):
    pass


# Functions & classes =========================================================
class SatusMessage(Persistent):
    def __init__(self, message, timestamp):
        self.message = message.strip()
        self.timestamp = timestamp

    def __eq__(self, obj):
        return self.message == obj.message and self.timestamp == obj.timestamp

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __hash__(self):
        return hash((self.timestamp, self.message))

    def __cmp__(self, obj):
        return self.timestamp.__cmp__(self, obj.timestamp)


class StatusInfo(Persistent):
    def __init__(self, rest_id, pub_url=None, registered_ts=None):
        self.rest_id = rest_id
        self.pub_url = pub_url
        self.messages = set()
        self.registered_ts = registered_ts

        if not registered_ts:
            self.registered_ts = time.time()

    def add_status_message(self, status_message):
        self.messages.add(status_message)

    def add_message(self, message, timestamp):
        self.add_status_message(
            SatusMessage(message, timestamp)
        )

    def get_messages(self):
        return sorted(self.messages, key=lambda x: x.timestamp)

    def __eq__(self, obj):
        return self.rest_id == obj.rest_id and self.messages == obj.messages

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __cmp__(self, obj):
        return self.registered_ts.__cmp__(self, obj.registered_ts)


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
                self.username_to_ids = uname_to_ids

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
            db_username = self.id_to_username.get(username, None)

            if not db_username:
                raise IndexError(
                    "Item '%s' is not registered to receive status updates for"
                    "'%s'!" % (username, rest_id)
                )

            if username != db_username:
                raise AccessDeniedException(
                    "Item '%s' is not owned by '%s'!" % (rest_id, username)
                )

            if not status_info_obj:
                return []

            return status_info_obj.get_messages()

    def query_statuses(self, username):
        with transaction.manager:
            uname_to_ids = self.username_to_ids.get(username, None)

            if uname_to_ids is None:
                raise ValueError(
                    "Username '%s' is not registered for tracking!" % username
                )

            return [
                status_update.get_messages()
                for status_update in sorted(
                    uname_to_ids,
                    key=lambda x: x.registered_ts
                )
            ]

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
