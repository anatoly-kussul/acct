#!/usr/bin/env bash
psql -h postgres -U postgres -w -c "CREATE USER eblank WITH PASSWORD 'i_am_password';"
psql -h postgres -U postgres -w -c "CREATE DATABASE eblank;"
psql -h postgres -U postgres -w -c "GRANT ALL PRIVILEGES ON DATABASE eblank to eblank;"