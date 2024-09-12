#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t seismic_server ${BASE}/seismic_server
docker service update --force --update-order start-first seismic_server
