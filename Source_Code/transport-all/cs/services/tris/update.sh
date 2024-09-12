#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t tris_server ${BASE}/tris_server
docker service update --force --update-order start-first tris_server
