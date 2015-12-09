#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import random
from functools import total_ordering

import transaction
from persistent import Persistent
from BTrees.OOBTree import OOSet

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler

from ..settings import PROJECT_KEY
from ..settings import ZEO_CLIENT_CONF_FILE


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
        """
        Constructor.

        Args:
            message (str): See :attr:`message` for details.
            timestamp (float): See :attr:`timestamp` for details.
        """
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
        book_name (str): Name of the book in human readable form.
        messages (list): List of :class:`StatusMessage` objects.
        registered_ts (float): Python timestamp format.
    """
    def __init__(self, rest_id, pub_url=None, book_name=None,
                 registered_ts=None):
        """
        Constructor.

        Args:
            rest_id (str): See :attr:`rest_id`.
            pub_url (str, default None): See :attr:`pub_url`.
            book_name (str, default None): See :attr:`book_name`.
            registered_ts (float, default None): See :attr:`registered_ts`. If
                not set, current time is used.
        """
        self.rest_id = rest_id
        self.pub_url = pub_url
        self.book_name = book_name
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
            list: :class:`.StatusMessage` instances.
        """
        return sorted(self.messages, key=lambda x: x.timestamp)

    def __eq__(self, obj):
        if not isinstance(obj, StatusInfo):
            return False

        return self.rest_id == obj.rest_id and self.messages == obj.messages

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __lt__(self, obj):
        return self.registered_ts.__lt__(obj.registered_ts)


class StatusHandler(DatabaseHandler):
    """
    Database handler for tracking :class:`StatusInfo` and
    :class:`StatusMessage` objects sent tru AMQP.
    """
    def __init__(self, conf_path=ZEO_CLIENT_CONF_FILE,
                 project_key=PROJECT_KEY):
        """
        Constructor.

        Args:
            conf_path (str): Path to the file with ZEO client configuration.
                Default :attr:`.ZEO_CLIENT_CONF_FILE`.
            project_key (str): Key used to access the ZEO `root`. Default
                :attr:`.PROJECT_KEY`.
        """
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

        # index for log
        self.log_key = "status log"
        self.log_db = self._get_key_or_create(
            self.log_key
        )

    def log(self, msg, session=None):
        """
        Log the message to the database.

        Args:
            msg (str): Content of the message.
            session (str): Optional session number used as prefix for message.
        """
        if session:
            msg = str(session) + ": " + msg

        self.log_db[time.time()] = msg

    @transaction_manager
    def register_status_tracking(self, username, rest_id):
        """
        Register `username` for tracking states of given `rest_id`.

        Args:
            username (str): Name of the user.
            rest_id (str): Unique identificator of given REST request.
        """
        self.log("Registering user '%s' to track '%s'." % (username, rest_id))

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

    @transaction_manager
    def save_status_update(self, rest_id, message, timestamp, book_name=None,
                           pub_url=None):
        """
        Save new status `message` to given `rest_id`.

        Warning:
            If the tracking for given user wasn't registered using
            :meth:`.register_status_tracking`, the status updates for this
            user / rest_id will be ignored!

        Args:
            rest_id (str): Unique identificator of given REST request.
            message (str): Content of the status update.
            timestamp (float): Python timestamp format.
            pub_url (str, default None): URL of the publication in edeposit.
        """
        status_info_obj = self.status_db.get(rest_id, None)

        # if the `rest_id` is not registered for tracking, just ignore it
        if not status_info_obj:
            return

        if pub_url:
            status_info_obj.pub_url = pub_url

        if book_name:
            status_info_obj.book_name = book_name

        status_info_obj.add_message(message, timestamp)

    @transaction_manager
    def query_status(self, rest_id, username=None):
        """
        List all messages stored in given `rest_id` for given `username`.

        Args:
            rest_id (str): Unique identificator of given REST request.
            username (str, default None): Name of the user. If not set, the
                username will not be checked.

        Raises:
            IndexError: If the user wasn't registered to receive status
                updates.
            AccessDeniedException: If the optional parameter `username` doesn't
                fit to given `rest_id`.

        Returns:
            obj: :class:`StatusInfo` for given `rest_id`.
        """
        status_info_obj = self.status_db.get(rest_id, None)
        db_username = self.id_to_username.get(rest_id, None)

        if not db_username:
            raise IndexError(
                "ID '{}' is not registered to receive status updates.".format(
                    rest_id
                )
            )

        if username and username != db_username:
            raise AccessDeniedException(
                "Item '%s' is not owned by '%s'!" % (rest_id, username)
            )

        if not status_info_obj:
            return []

        return status_info_obj.get_messages()

    @transaction_manager
    def query_statuses(self, username):
        """
        Get informations about all trackings for given `username`.

        Args:
            username (str): Selected username.

        Raises:
            IndexError: If username was not found in database.

        Returns:
            list: List of :class:`StatusInfo` objects sorted by creation time.
        """
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

        return sorted(status_infos, key=lambda x: x.registered_ts)

    @transaction_manager
    def remove_status_info(self, rest_id, username=None):
        """
        Stop tracking of given `rest_id`.

        Args:
            rest_id (str): Unique identificator of given REST request.
            username (str, default None): Name of the user. If not set, the
                username will not be checked.

        Raises:
            AccessDeniedException: In case that optional `username` parameter
                doesn't match with given `rest_id`.
        """
        session = random.randint(0, 100000)
        self.log("Request to remove StatusInfo(%s)." % repr(rest_id), session)

        # check privileges of `username` to access `rest_id`
        if username:
            if rest_id not in self.username_to_ids.get(username, []):
                self.log(
                    "Removing StatusInfo(%s): " % repr(rest_id) +
                    "Invalid username '%s'." % username,
                    session
                )

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
            del self.id_to_username[rest_id]
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

        self.log("StatusInfo(%s) successfully removed." % rest_id, session)

    @transaction_manager
    def remove_user(self, username):
        """
        Remove tracking of the `username`.

        If the `username` is not registered, than nothing happens.

        Args:
            username (str): Name of the user. If the user is not registered,
                then it is ignored.
        """
        ids = list(self.username_to_ids.get(username, None))

        if ids is None:
            return

        for rest_id in ids:
            self.remove_status_info(rest_id)

    def trigger_garbage_collection(self, interval=YEAR/2):
        """
        Do a garbage collection run and remove all :class:`StatusInfo` objects
        which are stored longer than `interval`.

        Args:
            interval (int/float): Inteval in seconds. Default YEAR/2.
        """
        with transaction.manager:
            garbage_rest_ids = [
                status_info.rest_id
                for status_info in self.status_db.values()
                if status_info.registered_ts + interval <= time.time()
            ]

            self.log(
                "Garbage collection triggered. Cleaning %d objects: %s" % (
                    len(garbage_rest_ids),
                    ", ".join(garbage_rest_ids)
                )
            )

        for rest_id in garbage_rest_ids:
            self.remove_status_info(rest_id)

        with transaction.manager:
            self.zeo.pack()
