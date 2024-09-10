#!/bin/bash


if [ "$#" -ne 2 ]; then
    echo "[-]Usage: ./collect_source_code.sh <IP> <remote directory>"
    exit
fi


# Init params
USER="cybernet"
REMOTE_IP=$1
REMOTE_DIR=$2
BASENAME=$(basename $REMOTE_DIR)


function run_semgrep() {

    SEMGREP_OUTPUT_DIRECTORY="Semgrep_$BASENAME"
    mkdir $SEMGREP_OUTPUT_DIRECTORY
    echo "[+]Start semgrep..."
    semgrep --output scan_results.json --json


}





function get_source_code() {
    
    echo "[+]Get source code of the mission"
    scp -r $USER@$REMOTE_IP:$REMOTE_DIR .

}



function push_to_github() {

    git add .
    git commit -m "Get source code and run semgrep for $BASENAME mission"
    git push origin main

}

# echo $BASENAME
# cd ./$BASENAME



# mv scan_results.json "../$SEMGREP_OUTPUT_DIRECTORY"
# cd ..


