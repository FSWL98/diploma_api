#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
flask db upgrade
uwsgi --ini ./uwsgi.ini --logto ./logs/uwsgi.log
