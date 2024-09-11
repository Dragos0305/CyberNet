#!/bin/bash

# ---------------------------------------------------------------
# Battery Information Service - Power Monitoring & Management
# ---------------------------------------------------------------
# This service retrieves detailed data for an array of batteries.
# Basic information such as battery ID, capacity, and type is
# publicly available for all users.
#
# 🔐 Authenticated Users Only:
#
# The field `energy_stored` provides the current energy stored in 
# each battery, measured in Watt-hours (Wh). As this data is 
# sensitive it is only to authenticated users.
#
# ---------------------------------------------------------------


while getopts u:p: flag
do
    case "${flag}" in
        u) username=${OPTARG};;
        p) password=${OPTARG};;
    esac
done

host=${@:$OPTIND:1}

if [ -z "$host" ]
then
    echo "Usage: $0 [-u username] [-p password] host"
    exit 1
fi


echo "[power] connecting to server: $host"
if ! [ -z "$username" ] && ! [ -z "$password" ]
then
    echo "[power] authenticating with username/password"
    # Note: incorrect authentication will result in a protocol error
    mosquitto_sub -h ${host} -p 46630 -t battery -u ${username} -P ${password} -V mqttv5 -k 5 -v 
else
    mosquitto_sub -h ${host} -p 46630 -t battery -V mqttv5 -k 5 -v
fi
