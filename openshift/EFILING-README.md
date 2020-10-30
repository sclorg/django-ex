## Installing Redis:

Open eDivorce App (test) in The OpenShift Application Console

Select "Add to Project" from the top right corner, then "Import YAML/JSON"

Paste the Redis template from https://raw.githubusercontent.com/bcgov/eDivorce/master/openshift/templates/redis/redis-deploy.yaml and click Create, then check "Process the template"

(use the default parameters unless you want to change the memory or storage allocation)


## Repeat for ClamAV:

https://raw.githubusercontent.com/bcgov/eDivorce/master/openshift/templates/clamav/clamav-deploy.json

## Adding new Environment variabales: 

Go to "Resources" => Secrets

Click "Create Secret"
- Secret Type = Generic Secret
- Secret Name = keycloak-secrets

Add the following two values:
- edivorce-client-secret : [GUID WILL BE PROVIDED]
- efiling-client-secret : [GUID WILL BE PROVIDED]

Go to "Applications" => Deployments => edivorce-django

Select the "Environment" tab.

Click "Add Value from Config Map or Secret"
- name = REDIS_PASSWORD
- select a resource = "redis"
- select key = "database-password"

Click "Add Value from Config Map or Secret"
- name = EDIVORCE_KEYCLOAK_SECRET
- select a resource = "keycloak-secrets"
- select key = "edivorce-client-secrets"

Click "Add Value from Config Map or Secret"
- name = EFILING_HUB_KEYCLOAK_SECRET
- select a resource = "keycloak-secrets"
- select key = "efiling-client-secrets"
