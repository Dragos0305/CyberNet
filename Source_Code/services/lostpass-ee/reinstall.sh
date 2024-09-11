#!/bin/bash

echo "This will cause some downtime, are you sure you want to continue? Press enter to continue or CTRL+C to cancel"
read ACCEPT

set -euxo pipefail

sudo apt install -y sass

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t lostpass-ee ${BASE}/lostpass-ee
docker stack rm lostpass-ee || true
while docker network inspect lostpass-ee_default >/dev/null 2>&1 ; do sleep 1; done
docker stack deploy --compose-file ${BASE}/docker-compose.yml lostpass-ee
${BASE}/wait-for-it.sh localhost:55099 -t 90
