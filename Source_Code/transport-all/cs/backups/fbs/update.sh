#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t fbs_server ${BASE}/fbs_server
docker service update --force --update-order start-first fbs_server
