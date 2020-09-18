## Installing Redis:

Open eDivorce App (test) in The OpenShift Application Console

Select "Add to Project" from the top right corner, then "Import YAML/JSON"

Paste the Redis template from https://raw.githubusercontent.com/bcgov/eDivorce/master/openshift/templates/redis/redis-deploy.yaml and click Create, then check "Process the template"

(use the default parameters unless you want to change the memory or storage allocation)


## Repeat for ClamAV:

https://raw.githubusercontent.com/bcgov/eDivorce/master/openshift/templates/clamav/clamav-deploy.json

## Adding new Environment variabales: 

Go to "Applications" => Deployments => edivorce-django

Select the "Environment" tab.

Add 2 new environment variables:

REDIS_HOST=redis
CLAMAV_TCP_ADDR=clamav

Click "Add Value from Config Map or Secret"

name = REDIS_PASSWORD
select a resource = "redis"
select key = "database-password"