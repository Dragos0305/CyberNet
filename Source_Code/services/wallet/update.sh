#!/bin/bash

set -euxo pipefail

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

docker build -t wallet_server ${BASE}/wallet_server
docker service update --force --update-order start-first wallet_server
