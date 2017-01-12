#!/usr/bin/env python
# -*- coding: utf-8 -*-


from os import path

BASE_DIR = path.dirname(path.abspath(__file__))
STATSD_FILE = BASE_DIR + '/statsd.yaml'

USERNAME = "admin"
PASSWORD = "admin"
PORT = 15672
STEP = 10

try:
    import socket

    HOSTNAME = socket.gethostname()
except Exception:
    import commands

    HOSTNAME = commands.getoutput("hostname")

FALCON_API = "http://127.0.0.1:1988/v1/push"
