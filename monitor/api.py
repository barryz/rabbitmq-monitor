#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: barryz
@mail: barryzxb@gmail.com
"""

import os
import sys
import json
import socket
import logging
from requests import auth, request


class RabbitMQAPIError(Exception):
    pass


class RabbitMQAPI(object):
    ''' RabbitMQ API
    '''
    def __init__(self, username='guest', password='guest', hostname='127.0.0.1', port=15672, protocol='http'):
        self.username = username
        self.password = password
        self.hostname = hostname or socket.gethostname()
        self.protocol = protocol
        self.port = port

    def call_api(self, **kwargs):
        url_prefix = '{0}://{1}:{2}/api/{3}'
        path = 'path' in kwargs and kwargs['path'] or ""
        payload = 'data' in kwargs and kwargs['data'] or None
        method = 'method' in kwargs and kwargs['method'] or "GET"
        url = url_prefix.format(self.protocol,
                                self.hostname,
                                self.port,
                                path
                                )

        if payload and method in ["POST", "PUT"]:
            headers = {"Content-Type": "application/json"}
        else: 
            headers = None

        try:
            r = request(method, url, headers=headers, data=payload, auth=(self.username, self.password)) 
        except Exception as e:
            raise RabbitMQAPIError(e)

        if r.status_code in [200, 204]: 
            return r
        else:
            raise RabbitMQAPIError("api call failed. {}: {}".format(r.status_code, r.reason))

        return 


def set_log(level, filename='options.log'):
    log_file = filename
    if not os.path.isfile(log_file):
        os.mknod(log_file)
        os.chmod(log_file, 0o644)
    log_level_total = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARN, 'error': logging.ERROR,
                       'critical': logging.CRITICAL}
    logger_f = logging.getLogger('rmqmonitor')
    logger_f.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger_f.addHandler(fh)
    return logger_f
