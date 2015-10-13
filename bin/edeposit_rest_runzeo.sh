#! /usr/bin/env bash

cd `python -c "import edeposit.amqp.rest.settings as s; print s.ZCONF_PATH"`

# supervisord can't stop the script, this should fix it
trap "{ pkill runzeo -SIGINT; exit 0; }" EXIT

runzeo -C zeo.conf
