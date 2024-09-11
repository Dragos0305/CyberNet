#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t power_server ${BASE}/power_server
docker service update --force --update-order start-first power_server
