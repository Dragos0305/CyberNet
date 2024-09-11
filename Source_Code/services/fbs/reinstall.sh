#!/bin/bash

echo "This will cause some downtime, are you sure you want to continue? Press enter to continue or CTRL+C to cancel"
read ACCEPT

set -euxo pipefail
mkdir -p /cs/data/fbs/server
mkdir -p /cs/data/fbs/redis
touch /cs/data/fbs/redis/import.sh

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

sudo apt-get install -yq php php-curl

docker build -t fbs_server ${BASE}/fbs_server
docker stack rm fbs || true
while docker network inspect fbs_default >/dev/null 2>&1 ; do sleep 1; done
docker stack deploy --compose-file ${BASE}/docker-compose.yml fbs
${BASE}/wait-for-it.sh localhost:8880 -t 90
