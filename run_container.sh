#!/bin/bash

CONTAINER_NAME="nonsense-sentiment-scraper"
IMAGE_NAME="nonsense-sentiment-scraper"
TAG="0.1"

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker start -ai $CONTAINER_NAME
else
  docker run -dit --name $CONTAINER_NAME \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/output:/app/output" \
    $IMAGE_NAME:$TAG
  docker attach $CONTAINER_NAME
fi

exit 0