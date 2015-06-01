#!/bin/bash

# Use this script to run one-off commands inside a container of a pod where your
# Python application code lives in.

# You can accomplish the same results by using regular commands from OpenShift.
# This script is just wrapping calls to `osc` to make it a little more
# convenient to use. In the future, the `osc` cli tool might incorporate changes
# that make this script obsolete.

# Here is how you would run a command in a pod specified by label [1]:
#
# 1. Inpect the output of the command below to find the name of a pod that
#    matches a given label:
#
#     osc get pods -l <your-label-selector>
#
# 2. Open a bash shell in the pod of your choice:
#
#     osc exec -p <pod-name> -it -- bash
#
# 3. Because of how `kubectl exec` and `osc exec` work right now [2], your
#    current working directory is root (/). Change it to where your code lives:
#
#     cd $HOME
#
# 4. Because of how the images produced with CentOS and RHEL work currently [3],
#    you need to manually enable any Software Collections you need to use:
#
#     source scl_source enable python33
#
# 5. Finally, execute any command that you need and exit the shell.
#
# Related GitHub issues:
# [1] https://github.com/GoogleCloudPlatform/kubernetes/issues/8876
# [2] https://github.com/GoogleCloudPlatform/kubernetes/issues/7770
# [3] https://github.com/openshift/origin/issues/2001


# You can use this wrapper like this:
#
#     ./run-in-container.sh ./manage.py migrate
#     ./run-in-container.sh ./manage.py createsuperuser
#     ./run-in-container.sh tail -f access.log
#
# If your Python pods are labeled with a name other than "web", you can use:
#
#     POD_NAME=something ./run-in-container.sh ./manage.py check
#
# You can also specify a POD by index:
#
#     POD_INDEX=1 ./run-in-container.sh tail -f access.log
#
# Or both together:
#
#     POD_NAME=frontend POD_INDEX=2 ./run-in-container.sh tail -f access.log


# Get name of a currently deployed pod by label and index
POD_INSTANCE_NAME=`osc get pods \
  -l "name=${POD_NAME:-web}" \
  -t "{{ with index .items ${POD_INDEX:-0} }}{{ .metadata.name }}{{ end }}"`

# Run command in a container of the specified pod:
osc exec -p "$POD_INSTANCE_NAME" -it -- bash -c \
  "cd \$HOME && source scl_source enable python33 && ${@:-echo}"
