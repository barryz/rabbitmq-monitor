#!/bin/bash
#


main_prog='mqm.py'
pid_file='mqm.pid'


function start() {
    /usr/bin/python ./${main_prog} &>/dev/null &
    pid=$(pgrep -f ${main_prog})
    echo $pid > ./${pid_file}
}


function stop() {
    curr_pid=$(pgrep -f ${main_prog})
    skill -9 ${curr_pid}
    if test $? -ne 0; then
        cat ${pid_file} | xargs -i skill -9 {}
    fi
}


function restart() {
    stop
    sleep 1
    start
}


function status() {
    pgrep -f ${main_prog} &>/dev/null
    if test $? -eq 0; then
        echo "running"
    else
        echo "not running"
    fi
}


function help() {
    echo "$0 |start|stop|restart|status|"
}


if [ "$1" == "" ]; then
    help
elif [ "$1" == "stop" ];then
    stop
elif [ "$1" == "start" ];then
    start
elif [ "$1" == "restart" ];then
    restart
elif [ "$1" == "status" ];then
    status
else
    help
fi
