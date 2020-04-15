#!/bin/bash

IMAGE_NAME="meepz0rk123"

sudo docker stop ${IMAGE_NAME} > /dev/null 2>&1 

sudo rm -Rf api/client
sudo rm -Rf api/server

sudo docker pull swaggerapi/swagger-codegen-cli
sudo docker pull swaggerapi/swagger-ui

# Generate the API Client 
sudo docker run --rm -v ${PWD}/api/:/api openapitools/openapi-generator-cli generate \
    -i /api/api.yaml \
    -g python \
    -o /api/client

# Generate the API Service
sudo docker run --rm -v ${PWD}/api:/api openapitools/openapi-generator-cli generate \
    -i /api/api.yaml \
    -g python-flask \
    -o /api/service

cp src/default_controller.py api/service/openapi_server/controllers/default_controller.py

# Build the Flask Server 
sudo docker build api/service/ -t $IMAGE_NAME 

# Run the Server
sudo docker run -it  -p 80:8080 -e SWAGGER_JSON=/api/api.json -v ${PWD}/api:/api ${IMAGE_NAME}:latest 



