#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
from monitor.statsd_client import StatsdClient
from monitor.api import set_log
from monitor.collector import RabbitmqInfo
from monitor.falcon import Falcon, FalconError
from config.config import HOSTNAME, USERNAME, PASSWORD, STEP, FALCON_API, PORT, STATSD_FILE
from utils.common import load_yaml_data


step = STEP
hostname = HOSTNAME
username = USERNAME
password = PASSWORD
port = PORT
len_limit = 30
falcon_api = FALCON_API
counterType = "GAUGE"
logger = set_log("error", "/tmp/rmqmon.log")


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
    lens = len(payload)
    f = Falcon(falcon_api)

    # 单次push限制30条metrics
    if lens > len_limit:
        offset = lens % len_limit
        for i in range(0, lens-1, len_limit):
            if i+len_limit-1 >= lens:
                to_send = payload[i:offset+i-1]
            else:
                to_send = payload[i:len_limit+i-1] 
            try:
                f.push(to_send)
            except FalconError as e:
                logger.error("push data to tranfer failed" + str(e))
    else:
        try:
            f.push(payload)
        except FalconError as e:
            logger.error("push data to tranfer failed" + str(e))


class StatsDHandlers(object):
    def __init__(self, filename=None, prefix=None):
        self.filename = filename
        self.prefix = prefix

    def load_statsd_conf(self):
        data = load_yaml_data(self.filename)
        statsd_host = data.get('host', '')
        statsd_port = data.get('port', 8125)
        return statsd_host, statsd_port

    def _send_to_statsd(self):
        try:
            if self.qdata:
                for k, v in self.qdata.items():
                    k = HOSTNAME + '.'
                    self.statsd_client.gauge(k, v)
            logger.info("Successfully send %d metrics to StatsD!", len(self.qdata))
        except Exception as e:
            logger.error(e)

    def _parse(self):
        self.qdata = {}
        for m in overview_info._fields:
            qdata[m] = "rabbitmq.queue.%s" % (m)
        return self._send_to_statsd()

    def __call__(self, *args, **kwargs):
        if self.filename:
            statsd_host, statsd_port = self.load_statsd_conf()
            self.statsd_client = StatsdClient(statsd_host, statsd_port, self.prefix)()
            return self._parse()


def main():
    try:
        push_statsd = StatsDHandlers(STATSD_FILE)
        while 1:
            try:
                fetch_mq_info()
                push_falcon()
                push_statsd()
            except Exception as e:
                logger.error("error occured when handle data " + str(e))
                time.sleep(step)
                continue
            time.sleep(step)
    except (Exception, KeyboardInterrupt, SystemExit) as e:
        logger.error("error occured in main program " + str(e))


if __name__ == "__main__":
    main()
