#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
Module is containing all necessary global variables for the package.

Module also has the ability to read user-defined data from two paths:

- ``$HOME/_SETTINGS_PATH``
- ``/etc/_SETTINGS_PATH``

See :attr:`_SETTINGS_PATH` for details.

Note:
    If the first path is found, other is ignored.

Example of the configuration file (``$HOME/edeposit/rest.json``)::

    {
        "WEB_ADDR": "0.0.0.0",
        "WEB_PORT": 80
    }

Attributes
----------
"""
# Imports =====================================================================
import os
import json
import os.path


# Module configuration ========================================================
ZEO_CLIENT_CONF_FILE = ""  #: Path to the ZEO configuration.
ZEO_SERVER_CONF_FILE = ""  #: Path to the ZEO configuration.
PROJECT_KEY = "edeposit_rest"  #: Don't change this!

WEB_ADDR = "localhost"  #: Address where the webserver should listen.
WEB_PORT = 8080  #: Port for the webserver.
WEB_SERVER = 'paste'  #: Use `paste` for threading.
WEB_DB_TIMEOUT = 30  #: How often should web refresh connection to DB.
WEB_DEBUG = False
WEB_RELOADER = False

WEB_CACHE = ""  #: Cache for the WEB upload.


# User configuration reader (don't edit this) =================================
_ALLOWED = [str, unicode, int, float, long, bool]  #: Allowed types.
_SETTINGS_PATH = "edeposit/rest.json"  #: Appended to default search paths.


def _get_all_constants():
    """
    Get list of all uppercase, non-private globals (doesn't start with ``_``).

    Returns:
        list: Uppercase names defined in `globals()` (variables from this \
              module).
    """
    return [
        key for key in globals().keys()
        if all([
            not key.startswith("_"),          # publicly accesible
            key.upper() == key,               # uppercase
            type(globals()[key]) in _ALLOWED  # and with type from _ALLOWED
        ])
    ]


def _substitute_globals(config_dict):
    """
    Set global variables to values defined in `config_dict`.

    Args:
        config_dict (dict): dict with data, which are used to set `globals`.

    Note:
        `config_dict` have to be dictionary, or it is ignored. Also all
        variables, that are not already in globals, or are not types defined in
        :attr:`_ALLOWED` (str, int, ..) or starts with ``_`` are silently
        ignored.
    """
    constants = _get_all_constants()

    if type(config_dict) != dict:
        return

    for key, val in config_dict.iteritems():
        if key in constants and type(val) in _ALLOWED:
            globals()[key] = val


def _read_from_paths():
    """
    Try to read data from configuration paths ($HOME/_SETTINGS_PATH,
    /etc/_SETTINGS_PATH).
    """
    home = os.environ.get("HOME", "/")
    home_path = os.path.join(home, _SETTINGS_PATH)
    etc_path = os.path.join("/etc", _SETTINGS_PATH)

    read_path = None
    if home and os.path.exists(home_path):
        read_path = home_path
    elif os.path.exists(etc_path):
        read_path = etc_path

    if read_path:
        with open(read_path) as f:
            _substitute_globals(
                json.loads(f.read())
            )


_read_from_paths()


# Checks ======================================================================
def _format_error(var_name, msg):
    msg = repr(msg) if msg else "UNSET!"
    return "You have to set %s (%s) in rest.json config!" % (var_name, msg)


def _assert_pattern(var_name):
    assert globals()[var_name], _format_error(var_name, globals()[var_name])


_assert_pattern("WEB_CACHE")
_assert_pattern("ZEO_CLIENT_CONF_FILE")
_assert_pattern("ZEO_SERVER_CONF_FILE")

assert os.access(WEB_CACHE, os.W_OK)
assert os.access(ZEO_CLIENT_CONF_FILE)
assert os.access(ZEO_SERVER_CONF_FILE)
