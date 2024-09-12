#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t camera_server ${BASE}/camera_server
docker service update --force --update-order start-first camera_server
