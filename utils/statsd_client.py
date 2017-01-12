#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
Author: Rosen
Mail: rosenluov@gmail.com
File: statsd_client.py
Created Time: Thu Jan 12 15:02:58 2017
"""

import statsd


class StatsdClient(object):
    def __init__(self, host, port, prefix=None):
        self.host = host
        self.port = port
        self.prefix = prefix

    def __call__(self):
        statsd_client = statsd.StatsClient(self.host, self.port, self.prefix)
        return statsd_client
