#!/bin/bash

while :
do
    redis-cli -h redis -p 6379 quit
    if [ $? -eq 0 ]; then
        cat /data/database.redis | redis-cli -h redis -p 6379 --pipe
        break
    else
        echo "Waiting for redis ..."
        sleep 2
    fi
done
