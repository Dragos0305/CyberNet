#!/bin/bash

echo "This will cause some downtime, are you sure you want to continue? Press enter to continue or CTRL+C to cancel"
read ACCEPT

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

which sqlite3 || bash -c "apt update && apt install -yq sqlite3"

docker build -t xflow_server ${BASE}/xflow_server
docker stack rm xflow || true
while docker network inspect xflow_default >/dev/null 2>&1 ; do sleep 1; done
docker stack deploy --compose-file ${BASE}/docker-compose.yml xflow
${BASE}/wait-for-it.sh localhost:42657 -t 90
