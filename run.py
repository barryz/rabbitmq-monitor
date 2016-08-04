#!/usr/bin/env python
# coding: utf-8

import os, sys
import time
import signal
from main import main


pid_file = "/var/run/mqm.pid"


def record_pid():
    with open(pid_file, 'w') as f:
        f.write('%s' % os.getpid())

def start():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.close(0)
    sys.stdin = open('/dev/null')
    os.close(1)
    sys.stdout = open('/dev/null', 'w')
    os.close(2)
    sys.stderr = open('/dev/null', 'w')
    os.setsid()
    os.umask(0)
    record_pid()
    main()
        

def stop():
    pid = int(open(pid_file, 'r').read())
    os.kill(pid, signal.SIGTERM)
    os.remove(pid_file)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'start':
        start()
    else:
        stop()
