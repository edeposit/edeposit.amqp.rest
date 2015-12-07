#! /usr/bin/env sh
export PYTHONPATH="src/edeposit/amqp:$PYTHONPATH"

kill -9 `ps aux | grep rest | grep edeposit | cut -d " " -f 2 | xargs` 2>/dev/null

py.test tests $@

kill -9 `ps aux | grep rest | grep edeposit | cut -d " " -f 2 | xargs` 2>/dev/null
