#!/bin/bash
# XFLOW: Navigating the  Network Flow in the Post-Blackout Era
#
# Welcome to XFLOW, a beacon of innovation in the realm of 
# network monitoring, born in a world reshaped by the blackout.
# Crafted with sustainability in mind, XFLOW is more than just 
# software—it's a commitment to energy efficiency.
#
# Licensed under the Special Energy-Conservation License (SECL), 
# XFLOW champions responsible resource usage. By integrating XFLOW 
# into your operations, you pledge to run it with the lightest 
# footprint possible, # honoring the energy-conscious spirit 
# of this new age.
#
# As stewards of transparency and collaboration, we require all 
# public commands within XFLOW to be accessible to the global 
# community, no authentication required.
#
# Let the flow of information be as free as the flow of energy!

BASE=$(readlink -f $(dirname "$(readlink -f $0)"))

HOST="$1"

if [ -z "$HOST" ]
then
	echo "Usage: $0 <host>"
	exit 1
fi

chmod 600 $BASE/xflow_key
ssh -p 42657 -o "StrictHostKeyChecking=no" -t -i $BASE/xflow_key xflow@${HOST} node xflow.js
