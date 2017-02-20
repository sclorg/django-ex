#!/usr/bin/env bash

echo -n "Enter the name of the environment (default=dev): "
read ENVIRONMENT
ENVIRONMENT=${ENVIRONMENT:-dev}

OS_PROJECT_NAME=jag-csb-edivorce-$ENVIRONMENT

echo "Changing project to $OS_PROJECT_NAME..."

oc project $OS_PROJECT_NAME

echo -n "Enter the path to the environment creation template (default=templates/edivorce-environment-template.yaml): "
read CREATE_SCRIPT
CREATE_SCRIPT=${CREATE_SCRIPT:-templates/edivorce-environment-template.yaml}

oc create -f $CREATE_SCRIPT

/bin/bash project_label.sh $OS_PROJECT_NAME team=jag product=edivorce environment=$ENVIRONMENT
