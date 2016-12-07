#!/usr/bin/env bash
script/init_postgres.sh
python -m eblank.main -v $RUN_ARGS