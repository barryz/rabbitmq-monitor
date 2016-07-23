#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
from monitor.api import set_log
from monitor.collector import RabbitmqInfo
from monitor.falcon import Falcon, FalconError
from config.config import HOSTNAME, USERNAME, PASSWORD, STEP, FALCON_API, PORT



step = STEP
hostname = HOSTNAME
username = USERNAME
password = PASSWORD
port = PORT
falcon_api = FALCON_API
counterType = "GAUGE"
logger = set_log("debug", "/tmp/rmqmon.log")


def fetch_mq_info():
    global overview_info, q_info
    mq = RabbitmqInfo(username, password, hostname, port)
    overview_info = mq.overview
    q_info = mq.queues


def push_falcon():
    payload = []
    ts = int(time.time())
    for m in overview_info._fields:
        ovdata = {}
        ovdata["time"] = ts
        ovdata["step"] = step
        ovdata["endpoint"] = hostname
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
            qdata["endpoint"] = hostname
            qdata["counterType"] = counterType
            qdata["metric"] = "rabbitmq.queue.%s" % (m)
            qdata["value"] = q.__getattribute__(m)
            qdata["tags"] = "name=%s,vhost=%s" % (q.name, q.vhost)
            payload.append(qdata)

    logger.info("get %s metrics" % (len(payload)))

    f = Falcon(falcon_api)
    try:
        f.push(payload)
    except FalconError as e:
        logger.error("push data to tranfer failed" + str(e))


def main():
    try:
        while 1:
            try:
                fetch_mq_info()
                push_falcon()
            except Exception as e:
                logger.error("error occured when handle data " + str(e))
                time.sleep(step)
                continue
            time.sleep(step)
    except (Exception, KeyboardInterrupt, SystemExit) as e:
        logger.error("error occured in main program " + str(e))
        

if __name__ == "__main__":
    main()
