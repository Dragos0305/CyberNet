#!/bin/bash

echo "This will cause some downtime, are you sure you want to continue? Press enter to continue or CTRL+C to cancel"
read ACCEPT

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

sudo apt install -y mosquitto-clients

docker build -t power_server ${BASE}/power_server
docker stack rm power || true
while docker network inspect power_default >/dev/null 2>&1 ; do sleep 1; done
docker stack deploy --compose-file ${BASE}/docker-compose.yml power
${BASE}/wait-for-it.sh localhost:46630 -t 90
