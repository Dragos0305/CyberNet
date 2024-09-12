#!/bin/bash
BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

if [ -n "$1" ]; then
    server=$1
else
    server=localhost
fi

chmod 600 $BASE/client_key
ssh -i $BASE/client_key -p 11356 -o "StrictHostKeyChecking=no" seismic@$server
