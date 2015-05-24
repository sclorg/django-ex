#!/bin/bash

# Use this script to run one-off commands inside a container of a pod
# (where your application code lives in)
#
# Examples:
# ./run-in-container.sh web date
# ./run-in-container.sh database env
# ./run-in-container.sh web ./manage.py migrate
# ./run-in-container.sh web ./manage.py createsuperuser
# ./run-in-container.sh web tail -f access.log
# POD_INDEX=1 ./run-in-container.sh web tail -f access.log

POD_NAME="$1"
if [[ -z "$POD_NAME" ]]; then
  echo "missing pod name"
  exit 1
fi
shift

quoted_args="$(printf " %q" "${@:-echo}")"
osc exec -p $(osc get pods -l "name=$POD_NAME" -t "{{ with index .items ${POD_INDEX:-0} }}{{ .metadata.name }}{{ end }}") -it -- bash -c "cd \$HOME && scl enable python33 \"$quoted_args\""

