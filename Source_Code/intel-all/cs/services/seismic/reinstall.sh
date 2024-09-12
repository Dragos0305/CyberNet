#!/bin/bash
BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

echo "This will cause some downtime, are you sure you want to continue? Press enter to continue or CTRL+C to cancel"
read ACCEPT

set -euxo pipefail

docker build -t seismic_server ${BASE}/seismic_server
docker stack rm seismic || true
while docker network inspect seismic_default >/dev/null 2>&1 ; do sleep 1; done
docker stack deploy --compose-file ${BASE}/docker-compose.yml seismic
${BASE}/wait-for-it.sh localhost:11356 -t 90
