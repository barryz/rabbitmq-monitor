#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
from monitor.api import set_log
from monitor.collector import RabbitmqInfo
from monitor.falcon import Falcon, FalconError
from config.config import HOSTNAME, USERNAME, PASSWORD, STEP, FALCON_API



step = STEP
hostname = HOSTNAME
username = USERNAME
password = PASSWORD
falcon_api = FALCON_API
counterType = "GAUGE"
logger = set_log("debug", "/tmp/rmqmon.log")


def fetch_mq_info():
    global overview_info, q_info
    mq = RabbitmqInfo(username, password, hostname)
    overview_info = mq.overview
    q_info = mq.queues


def push_falcon():
    payload = []
    ts = int(time.time())
    for m in overview_info._fields:
        ovdata = {}
        ovdata["time"] = ts
        ovdata["step"] = step
        ovdata["endpoint"] = HOSTNAME
        ovdata["counterType"] = counterType
        ovdata["metric"] = "rabbitmq.overview.%s" % (m)
        ovdata["value"] = overview_info.__getattribute__(m)
        ovdata["tags"] = ""
        payload.append(ovdata)

    for q in q_info:
        for m in q._fields:
            qdata = {}
            if m in ["name", "vhost"]:
                continue
            qdata["time"] = ts
            qdata["step"] = step
            qdata["endpoint"] = HOSTNAME
            qdata["counterType"] = counterType
            qdata["metric"] = "rabbitmq.queue.%s" % (m)
            qdata["value"] = q.__getattribute__(m)
            qdata["tags"] = "name=%s,vhost=%s" % (q.name, q.vhost)
            payload.append(qdata)

    f = Falcon(falcon_api)
    try:
        f.push(payload)
    except FalconError as e:
        logger.error("push data to tranfer failed" + str(e))


def main():
    try:
        while 1:
            fetch_mq_info()
            push_falcon()
            time.sleep(step)
    except (Exception, KeyboardInterrupt, SystemExit) as e:
        logger.error("program exit...")
        

if __name__ == "__main__":
    main()
