#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t xflow_server ${BASE}/xflow_server
docker service update --force --update-order start-first xflow_server
