#! /usr/bin/env bash

ZEO_PATH=`python - <<EOF
import sys
import os.path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/edeposit/amqp"))
try:
    from rest import settings
except ImportError:
    from edeposit.amqp.rest import settings

assert settings.ZEO_SERVER_CONF_FILE, settings._format_error(
    "ZEO_SERVER_CONF_FILE",
    settings.ZEO_SERVER_CONF_FILE
)

print settings.ZEO_SERVER_CONF_FILE
EOF
`

if [ $? == 1 ]; then
    exit 1;
fi

# supervisord can't stop the script, this should fix it
trap "{ pkill runzeo -SIGINT; exit 0; }" EXIT

runzeo -C $ZEO_PATH
