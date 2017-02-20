#!/usr/bin/env bash

# todo: this is an example from https://github.com/bcgov/esm-server/tree/develop/openshift
# todo: it needs to be completely reconfigured for eDivorce!!!!

#project_label.sh $OS_PROJECT_NAME category=$CATEGORY team=$TEAM product=$PRODUCT environment=$ENVIRONMENT

PROJECT_NAME=$1

echo "Project name is $1"

for i in "${@:2}"; do
    oc label --overwrite namespace/$PROJECT_NAME $i
done
