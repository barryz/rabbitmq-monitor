#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import json
import socket
from collections import namedtuple
from api import RabbitMQAPI, RabbitMQAPIError, set_log


logger = set_log("debug", "/tmp/rmqmon.log")


class RabbitmqInfo(object):
    """Fetch RabbitMQ statistics infomation.
       pramas:
       username: 
       password: username/password to access rabbitmq server.
       hostname: rabbitmq server hostname, default: local hostname.
    """
    metric_overview = namedtuple("overview", [
                                        "queuesTotal",
                                        "channlesTotal",
                                        "connectionsTotal",
                                        "consumersTotal",
                                        "exchangesTotal",
                                        "msgsTotal",
                                        "msgsReadyTotal",
                                        "msgsUnackTotal",
                                        "deliverTotal",
                                        "publishTotal",
                                        "redeliverTotal",
                                        "statsDbEvent",
                                        "deliverRate",
                                        "publishRate",
                                        "ackRate",
                                        "fdUsedPct",
                                        "memUsedPct",
                                        "socketUsedPct",
                                        "erlProcsUsedPct",
                                        "isAlive",
                                        "isPartition"
                                        ])
    metric_queue = namedtuple("queues", [
                                    "name",
                                    "messages",
                                    "messages_ready",
                                    "messages_unacked",
                                    "delver_get",
                                    "publish",
                                    "ack",
                                    "dpratio",
                                    "memory",
                                    "consumers",
                                    "consumer_utilisation",
                                    "status",
                                    "vhost"
                                    ])

    def __init__(self, user="guest", password="guest", hostname=socket.gethostname()):
        self.q = RabbitMQAPI(user, password, hostname)
        self.hostname = hostname

    @staticmethod
    def filter_queue(queue):
        test_strs = "test"
        invalid_vhosts = ["/", ""]
        return filter(lambda x: test_strs not in x.get("name", ""), 
                    filter(lambda x: not x.get("auto_delete", True), 
                    filter(lambda x: x.get("vhost", "") not in invalid_vhosts, queue)))

    @property
    def overview(self):
        hostname = "rabbit@{}".format(self.hostname)
        overviews = RabbitmqInfo.metric_overview
        try:
            overview = self.q.call_api(path="overview", method="GET")
            alive = self.q.call_api(path="/aliveness-test/%2f", method="GET")
            nodes = self.q.call_api(path="nodes/{}".format(hostname), method="GET")
        except RabbitMQAPIError as e:
            logger.error("error occured during call rabbitmq api."+str(e))
            return None
        overview, nodes, alive = json.loads(overview.text), json.loads(nodes.text), json.loads(alive.text)
        metrics_overview_struct = overviews(
                                            overview.get("object_totals", {}).get("queues", 0),
                                            overview.get("object_totals", {}).get("channels", 0),
                                            overview.get("object_totals", {}).get("connections", 0),
                                            overview.get("object_totals", {}).get("consumers", 0),
                                            overview.get("object_totals", {}).get("exchanges", 0),
                                            overview.get("queue_totals", {}).get("messages", 0),
                                            overview.get("queue_totals", {}).get("messages_ready", 0),
                                            overview.get("queue_totals", {}).get("messages_unacknowledged", 0),
                                            overview.get("message_stats", {}).get("deliver_get", 0),
                                            overview.get("message_stats", {}).get("publish", 0),
                                            overview.get("message_stats", {}).get("redeliver", 0),
                                            overview.get("statistics_db_event_queue", 0),
                                            overview.get("message_stats", {}).get("deliver_get_details", {}).get("rate", 0.0),
                                            overview.get("message_stats", {}).get("publish_details", {}).get("rate", 0.0),
                                            overview.get("message_stats", {}).get("ack_details", {}).get("rate", 0.0),
                                            round(float(nodes.get("fd_used", 0)) / float(nodes.get("fd_total", 655360)), 4),
                                            round(float(nodes.get("mem_used", 0)) / float(nodes.get("mem_limit", 102400000)), 4),
                                            round(float(nodes.get("sockets_used", 0)) / float(nodes.get("sockets_total", 589732)), 4),
                                            round(float(nodes.get("proc_used", 0)) / float(nodes.get("proc_total", 1048576)), 4),
                                            1 if not nodes.get("partitions", True) else 0,  
                                            1 if alive.get("status", True) else 0 
                                            )

        return metrics_overview_struct

    @property
    def queues(self):
        q_info = []
        metrics_queue_struct = RabbitmqInfo.metric_queue
        try:
            queues = self.q.call_api(path="/queues", method="GET")
        except RabbitMQAPIError as e:
            logger.error("error occured during call rabbitmq queues api."+str(e))       
            return None

        queues = self.filter_queue(json.loads(queues.text))

        for q in queues:
            deliver_rate = q.get("message_stats", {}).get("deliver_get_details", {}).get("rate", 0.0)
            publish_rate = q.get("message_stats", {}).get("publish_details", {}).get("rate", 0.0)
            ack_rate = q.get("message_stats", {}).get("ack_details", {}).get("rate", 0.0)

            try:
                dpratio = round(float(deliver_rate) / float(publish_rate), 3)
            except ZeroDivisionError:
                dpratio = 0.0

            status = q.get("state", "dead")
            if status not in ["idle", "running"]:
                status = 0
            else:
                status = 1

            q_info.append(metrics_queue_struct(
                                                q.get("name", "null"),
                                                q.get("messages", 0),
                                                q.get("messages_ready", 0),
                                                q.get("messages_unacknowledged", 0),
                                                deliver_rate,
                                                publish_rate, 
                                                ack_rate,
                                                dpratio,
                                                q.get("memory", 0.0),
                                                q.get("consumers", 0),
                                                q.get("consumer_utilisation", None) or 0.0,
                                                status,
                                                q.get("vhost", "null")
                                                ))

        return q_info
