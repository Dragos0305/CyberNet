# How to run a mission (fbs example)

## Prerequisites

```bash
docker
```

## Installation script for docker
```bash
#!/bin/bash

sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Init docker swarm
```bash
docker swarm init
```

## Build docker image for a specific service
```bash
# Example for fbs mission
cd /home/dragos/CyberNet/Source_Code/transport-all/cs/backups/fbs/fbs_server

docker build -t docker build -t fbs_server . # The name of the image must be the same with the name from docker-compose file

```

## Install dependencies for the client
```bash
sudo apt-get install -yq php php-curl
```

## Go to docker-compose file location
```bash
cd /home/dragos/CyberNet/Source_Code/transport-all/cs/backups/fbs
```

## Change volumes for data directory
```yaml
# Change the location of data from your machine
volumes:
    - /cs/data/fbs/server:/data:ro # line 11

volumes:
    - /cs/data/fbs/redis:/data:ro # line 22
    
volumes:
    - /cs/data/fbs/redis:/data:ro # line 37

# After modification
volumes:
    -/home/dragos/CyberNet/Source_Code/transport-all/cs/data/fbs/server:/data:ro

volumes:
    -/home/dragos/CyberNet/Source_Code/transport-all/cs/data/fbs/redis:/data:ro

volumes:
    -/home/dragos/CyberNet/Source_Code/transport-all/cs/data/fbs/redis:/data:ro

```
## Run deploy
```bash

# Go back to server directory from services and run deploy command
cd /home/dragos/CyberNet/Source_Code/transport-all/cs/backups/fbs

sudo docker stack deploy --compose-file ./docker-compose.yml fbs
# Output
Creating network fbs_default
Creating service fbs_redis
Creating service fbs_redis_setup
Creating service fbs_server
```

## Check status of the containers
```bash
sudo docker container ps -a
```

## Check with the client
```bash
./fbs_client.php [YOUR_IP] list

# Example
./fbs_client 192.168.171.144 list
./fbs_client.php localhost list
```
