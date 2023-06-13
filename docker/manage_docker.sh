#!/bin/bash
if [[ $1 == "--up" ]]; then
    docker-compose -f $(pwd)/1-kafka/docker-compose.yml up -d
    sleep 10
    docker-compose -f $(pwd)/2-spark/docker-compose.yml up -d
elif [[ $1 == "--down" ]]; then
    docker-compose -f $(pwd)/2-spark/docker-compose.yml down
    docker-compose -f$(pwd)/1-kafka/docker-compose.yml down
else
    echo "invalid command. [--up or --down]"
fi