#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t lostpass-ee ${BASE}/lostpass-ee
docker service update --force --update-order start-first lostpass-ee_lostpass-ee
