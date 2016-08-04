#!/usr/bin/env python
# -*- coding: utf-8 -*-


USERNAME="admin"
PASSWORD="admin"
PORT=15672
STEP=10

try:
    import socket
    HOSTNAME=socket.gethostname()
except Exception:
    import commands
    HOSTNAME=commands.getoutput("hostname")

FALCON_API = "http://127.0.0.1:1988/v1/push"
