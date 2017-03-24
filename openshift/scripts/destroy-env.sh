#!/usr/bin/env bash

# this is hard-coded to only destroy the dev environment
# you can chage it to 'test' or 'prod' if you are sure you want to destroy EVERYTHING, include the database
oc project jag-csb-edivorce-test

# delete all imagestreams
oc delete is --all

# delete services by name (we don't want to accidentally delete the gluster service!)
oc delete svc weasyprint
oc delete svc postgresql
oc delete svc edivorce-django

# delete routes
oc delete route --all

# delete persistent volume claims
oc delete pvc --all

# delete replication controllers
oc delete rc --all

# delete deployment configurations
oc delete dc --all

# delete pods
oc delete po --all
 No newline at end of file
