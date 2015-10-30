#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import transaction
from persistent import Persistent

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
    def __init__(self, rest_id, pub_url, registered_ts):
        self.rest_id = rest_id
        self.pub_url = pub_url
        self.messages = set()
        self.registered_ts = registered_ts

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
        self.status_id_key = "status_id"
        self.id_to_username = self._get_key_or_create(self.status_id_key)

    def register_status_tracking(self, username, rest_id):
        with transaction.manager:
            self.id_to_username[rest_id] = username

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
        pass

    def remove_status_info(self, rest_id):
        pass

    def garbage_collection(self, interval=YEAR/2):
        pass
