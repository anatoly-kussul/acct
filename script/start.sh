#!/usr/bin/env bash

trap 'kill -15 $PID' SIGTERM  # if script receives SIGTERM (default Docker action) this script will resend it to app

script/init_postgres.sh

python -m eblank.main -v $RUN_ARGS &
PID=$!
wait $PID  # wait for app to receive SIGTERM
wait $PID  # wait for app to gracefully shutdown
EXIT_STATUS=$?
