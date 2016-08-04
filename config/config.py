#!/usr/bin/env python
# -*- coding: utf-8 -*-


USERNAME="admin"
PASSWORD="On1NgXOoy3lLMO"
PORT=15672
STEP=10

'''
try:
    import socket
    HOSTNAME=socket.gethostname()
except Exception:
    import commands
    HOSTNAME=commands.getoutput("hostname")
'''
HOSTNAME = "xg-fanout-rmq-1"

FALCON_API = "http://127.0.0.1:1988/v1/push"
