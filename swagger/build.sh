#!/bin/bash

IMAGE_NAME="meepz0rk123"
CONTAINER_NAME="yadayada99"

sudo docker stop ${CONTAINER_NAME} > /dev/null 2>&1 
sudo docker rm ${CONTAINER_NAME} > /dev/null 2>&1
sudo docker rmi ${IMAGE_NAME} > /dev/null 2>&1

sudo rm -Rf api/client
sudo rm -Rf api/server

sudo docker pull swaggerapi/swagger-codegen-cli

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

sudo cp src/default_controller.py api/service/openapi_server/controllers/default_controller.py
sudo chmod ugo+w ./api/service/requirements.txt
sudo echo "pytest" >> ./api/service/requirements.txt
sudo echo "pytest-html" >> ./api/service/requirements.txt

# Build the Flask Server 
sudo docker build api/service/ -t $IMAGE_NAME 

# Run the Server
sudo docker run -d  -p 80:8080 -e SWAGGER_JSON=/api/api.json -v ${PWD}/api:/api -v ${PWD}/tests:/tests --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest 

echo "Test out the api here : http://localhost/practice/1.0.0/ui/"


