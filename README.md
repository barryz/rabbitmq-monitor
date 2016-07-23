RabbitMQ 状态数据采集脚本(用于OpenFalcon&Graphite监控系统)
-----------------------------------------------------------

## Requirement:
- os: Linux
- Python: >= 2.6
- Python依赖库: requests

-----------------------------------------------------------

## 原理
-----------------------------------------------------------
通过RabbitMQ REST API 获取MQ相关状态数据，然后整合固定数据类型，推送到不同的监控系统。

## 相关指标
------------------------------------------------
- **overview指标**

| key | tag | type | note |
|-----|-----|------|------|
|rabbitmq.overview.publishRate| |GAUGE|生产总速率|
|rabbitmq.overview.deliverRate| |GAUGE|消费总速率|
|rabbitmq.overview.ackRate| |GAUGE|消费者确认总速率|
|rabbitmq.overview.msgsTotal| |GAUGE|消息总数, 等于ready + unack|
|rabbitmq.overview.msgsReadyTotal| |GAUGE|消息堆积总数|
|rabbitmq.overview.msgsUnackTotal| |GAUGE|消费未确认消息总数|
|rabbitmq.overview.publishTotal| |GAUGE|生产消息总数|
|rabbitmq.overview.deliverTotal| |GAUGE|投递消息总数|
|rabbitmq.overview.redeliverTotal| |GAUGE|重新投递消息总数|
|rabbitmq.overview.channlesTotal| |GAUGE|Channel 总数|
|rabbitmq.overview.connectionsTotal| |GAUGE|Connection 总数|
|rabbitmq.overview.consumersTotal| |GAUGE|Counsumer总数|
|rabbitmq.overview.queuesTotal| |GAUGE|队列总数|
|rabbitmq.overview.exchangesTotal| |GAUGE|exchange 总数|
|rabbitmq.overview.isAlive| |GAUGE|MQ健康状态|
|rabbitmq.overview.isPartition| |GAUGE|MQ集群网络分区状态|
|rabbitmq.overview.memUsedPct| |GAUGE|内存使用占比|
|rabbitmq.overview.fdUsedPct| |GAUGE|file desc使用占比|
|rabbitmq.overview.erlProcsUsedPct| |GAUGE|Erlang 进程使用占比|
|rabbitmq.overview.socketUsedPct| |GAUGE|socket使用占比|
|rabbitmq.overview.statsDbEvent| |GAUGE|状态统计数据库事件队列个数|


- **Queue指标**

| key | tag | type | note |
|-----|-----|------|------|
|rabbitmq.queue.publish|name=$queue-name,vhost=$vhost|GAUGE|该队列生产消息速率|
|rabbitmq.queue.delver_get|name=$queue-name,vhost=$vhost|GAUGE|该队列投递消息速率|
|rabbitmq.queue.ack|name=$queue-name,vhost=$vhost|GAUGE|该队列consumer确认消息速率|
|rabbitmq.queue.consumers|name=$queue-name,vhost=$vhost|GAUGE|该队列consumer个数|
|rabbitmq.queue.consumer_utilisation|name=$queue-name,vhost=$vhost|GAUGE|该队列消费利用率(消费能力)|
|rabbitmq.queue.dpratio|name=$queue-name,vhost=$vhost|GAUGE|该队列消费生产速率比|
|rabbitmq.queue.memory|name=$queue-name,vhost=$vhost|GAUGE|该队列所占内存字节数|
|rabbitmq.queue.messages|name=$queue-name,vhost=$vhost|GAUGE|该队列消息总数|
|rabbitmq.queue.messages_ready|name=$queue-name,vhost=$vhost|GAUGE|该队列等待被消费消息数|
|rabbitmq.queue.messages_unacked|name=$queue-name,vhost=$vhost|GAUGE|该队列消费未确认消息数|
|rabbitmq.queue.messages_status|name=$queue-name,vhost=$vhost|GAUGE|该队列状态(非idle/running,即认为不健康)|



## 使用方法
--------------------------------------
1. 修改config/config.py 里的USERNAME/PASSWORD/PORT ，修改为rabbitmq-server的管理用户和密码、管理端口
2. 确认是否该用户是否有对应vhost/queue权限


## 启动方式
--------------------------------------
````bash
$python main.py &>/dev/null &
````

## TODO

- 数据push到graphite
