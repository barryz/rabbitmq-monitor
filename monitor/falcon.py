#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json


class FalconError(Exception):
    pass


class Falcon(object):
    """A wrapper for Falcon-Agent push interface.
    """

    def __init__(self, url="http://127.0.0.1:1988/v1/push"):
        self.url = url

    def push(self, data):
        """params like:
            payload = [{
                    "endpoint": "hostname",
                    "metric": "metirc",
                    "timestamp": "ts",
                    "step": "step",
                    "value": "value",
                    "counterType": "GAUGE",
                    "tags": "queue=alliance,vhost=alliance"
                    },
                    ...
                ]
        """
        if not isinstance(data, list):
            raise FalconError("params must be a list object")
        
        try:
            r = requests.post(self.url, data=json.dumps(data))
        except Exception as e:
            raise FalconError("call agent api failed " + str(e))
            r = ""
        
        if (r and r.status_code == 200):
            return True
        else:
            raise FalconError("unexpected result")
