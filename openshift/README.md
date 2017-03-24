# A Quickstart Guide to Setting Up eDivorce on OpenShift

There are three deployment environments set up for different purposes within OpenShift. They are available at the URLs below.

|Environment| URL |Justice URL|
|-----------|-----|-----------|
|DEV|[https://edivorce-dev.pathfinder.gov.bc.ca]|[https://justice.gov.bc.ca/divorce-dev]|
|TEST|[https://edivorce-test.pathfinder.gov.bc.ca]|[https://justice.gov.bc.ca/divorce-test]|
|PROD|[https://edivorce-prod.pathfinder.gov.bc.ca]|[https://justice.gov.bc.ca/divorce]|

These instructions assume you have 4 EMPTY projects created in OpenShift:

- jag-csb-edivorce-tools (BUILD)
- jag-csb-edivorce-dev (DEV)
- jag-csb-edivorce-test (TEST)
- jag-csb-edivorce-prod (PROD)

## How to Access OpenShift for eDivorce

### Web UI
- Login to https://console.pathfinder.gov.bc.ca:8443; you'll be prompted for GitHub authorization.  You must be part of the BCDevOps Github organization, and you must have access to the eDivorce projects.

### Command-line (```oc```) tools
- Download OpenShift [command line tools](https://github.com/openshift/origin/releases/download/v1.2.1/openshift-origin-client-tools-v1.2.1-5e723f6-mac.zip), unzip, and add ```oc``` to your PATH.
- Copy command line login string from https://console.pathfinder.gov.bc.ca:8443/console/command-line.  It will look like ```oc login https://console.pathfinder.gov.bc.ca:8443 --token=xtyz123xtyz123xtyz123xtyz123```
- Paste the login string into a terminal session.  You are no authenticated against OpenShift and will be able to execute ```oc``` commands. ```oc -h``` provides a summary of available commands.


## Uploading Templates into OpenShift

1. Clone the project from Github, and then ```cd``` into the openshift/templates directory.

2. Log into the OpenShift console to get your command line token.  Then log into OpenShift from the command line.

3. Upload the templates into OpenShift with the following commands

    Tools templates
    ```
    oc create -f ../jenkins/jenkins-pipeline-persistent-template.json -n jag-csb-edivorce-tools
    oc create -f edivorce-build-template.yaml -n jag-csb-edivorce-tools
    oc create -f nginx-build-template.yaml -n jag-csb-edivorce-tools
    oc create -f ../jenkins/pipeline.yaml -n jag-csb-edivorce-tools
    ```

    Main eDivorce environment template
    ```
    oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-dev
    oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-test
    oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-prod
    ```

    NGINX proxy template
    ```
    oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-dev
    oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-test
    oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-prod
    ```

## Setting up the Tools Project

### Install Docker on your computer

### Build the S2I image:

```docker build -t s2i-nginx git://github.com/BCDevOps/s2i-nginx```

### Tag and push this image to the OpenShift Docker Registry for your OpenShift Project:

```
docker tag s2i-nginx docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx

docker login docker-registry.pathfinder.gov.bc.ca -u <username> -p <token>

docker push docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx
```

(your docker token is the same as your OpenShift login token)

###  Process the templates in the 'tools' project

#### These can be processed from the commandline
```
oc project jag-csb-edivorce-tools

oc process jenkins-pipeline-persistent | oc create -f -
oc process edivorce-build | oc create -f -
oc process nginx-build | oc create -f -
```

#### For some reason the edivorce-build-pipeline template can't be processed from the command line like the other templates

1. Log into the web console ang go to the :"eDivorce App (tools)" project

2. Select "Add to Project" from the web interface

3. On the Browse Catalog tab, type "edivorce-build-pipeline" into the filter field.  Select the template.

4. Create

5. Delete the extra services that OpenShift automatically created when you processed the edivorce-build-template. We are using perisistent storage for Jenkins.  These are ephemeral.

    ```
    oc project jag-csb-edivorce-tools

    oc delete svc jenkins-pipeline-svc
    oc delete deploymentconfig jenkins-pipeline-svc
    oc delete route jenkins-pipeline-svc
    ```

### Add the webhook to GitHub

1. Log into the web console ang go to the :"eDivorce App (tools)" project

2. Select Builds => Pipelines => build-and-deploy-to-dev => Configuration

3. Copy the GitHub wookhook URL

4. Go to the repository settings in Github, and add the webhook url under "Webhooks"
-- Payload URL = The URL you copied from OpenShift
-- Content type = application/json
-- Secret = Leave Blank
-- Just push the event
-- Active

## Setting up Dev/Test/Prod Projects

### Important Configuration Options

#### Mandatory Settings:

**PROXY_NETWORK:**

Network of upstream proxy. This is used to ensure that requests come from
the Justice Proxy only. It should be entered in IPV4 CIDR notation
e.g. 10.10.15.10/16. The actual value you need to enter cannot be stored on Github
because this would violate BC Government Github policies. The PROXY_NETWORK
setting is currently the same for all 3 environments (dev, test & prod)

#### Optional Settings you will probably want to set:

**BASICAUTH_ENABLED:**

Turns on simple basic authentication for test and dev environments.
This is recommended since these environments are accessible to the general public.
Set it to "True" (no quotes) to enable it.  Default = False

**BASICAUTH_USERNAME / BASICAUTH_PASSWORD:**

Username will default to divorce, and password will default to a random 16 digit string
unless you override these settings

### Setting up Dev

Tag the builds in the tools project so they can be deployed to dev
```
oc project jag-csb-edivorce-tools
oc tag edivorce-django:latest edivorce-django:deploy-to-dev
oc tag nginx-proxy:latest nginx-proxy:deploy-to-dev
```

Give the dev project access to Docker images stored in the tools project
```
oc project jag-csb-edivorce-dev
oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-dev:default -n jag-csb-edivorce-tools
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:default -n jag-csb-edivorce-dev
```

Deploy the Django app and the Postgresql DB
```
oc process edivorce -v ENVIRONMENT_TYPE=dev,PROXY_NETWORK=123.45.67.89/0,BASICAUTH_ENABLED=True | oc create -f -
```

Deploy the NGINX proxy
```
oc process nginx -v ENVIRONMENT_TYPE=dev | oc create -f -
```

Deploy Weasyprint
```
oc deploy weasyprint --latest
```

Give the Jenkins build pipeline access to the dev project
```
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:jenkins -n jag-csb-edivorce-dev
```


### Setting up Test

Tag the builds in the tools project so they can be deployed to test
```
oc project jag-csb-edivorce-tools
oc tag edivorce-django:latest edivorce-django:deploy-to-test
oc tag nginx-proxy:latest nginx-proxy:deploy-to-test
```

Give the test project access to Docker images stored in the tools project
```
oc project jag-csb-edivorce-test
oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-test:default -n jag-csb-edivorce-tools
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:default -n jag-csb-edivorce-test
```

Deploy the Django app and the Postgresql DB
```
oc process edivorce -v ENVIRONMENT_TYPE=test,PROXY_NETWORK=123.45.67.89/0,BASICAUTH_ENABLED=True | oc create -f -
```

Deploy the NGINX proxy
```
oc process nginx -v ENVIRONMENT_TYPE=test | oc create -f -
```

Deploy Weasyprint
```
oc deploy weasyprint --latest
```

Give the Jenkins build pipeline access to the test project
```
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:jenkins -n jag-csb-edivorce-test
```

### Setting up Prod

Tag the builds in the tools project so they can be deployed to prod
```
oc project jag-csb-edivorce-tools
oc tag edivorce-django:latest edivorce-django:deploy-to-prod
oc tag nginx-proxy:latest nginx-proxy:deploy-to-prod
```

Give the prod project access to Docker images stored in the tools project
```
oc project jag-csb-edivorce-prod
oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-prod:default -n jag-csb-edivorce-tools
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:default -n jag-csb-edivorce-prod
```

Deploy the Django app and the Postgresql DB
```
oc process edivorce -v ENVIRONMENT_TYPE=prod,PROXY_NETWORK=123.45.67.89/0 | oc create -f -
```

Deploy the NGINX proxy
```
oc process nginx -v ENVIRONMENT_TYPE=prod | oc create -f -
```

Deploy weasyprint
```
oc deploy weasyprint --latest
```

Give the Jenkins build pipeline access to the prod project
```
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:jenkins -n jag-csb-edivorce-prod
```


## Data management operations

If you need to access the DB, you can either use the terminal window in the OpenShift console or the ```oc rsh```
command to get to the command line on the postgresql pod.

### You can find the current name of the postgresql pod in the web console

The pod identifiers change with every deployment, you need to find the current one

```
oc rsh postgresql-2-qp0oh
```


### Sample postgresql terminal session
```
psql -d default

\dt

select count(*) from core_bceiduser;

\q

exit
```

## How to access Jenkins for eDivorce

- Login to https://edivorce-jenkins.pathfinder.gov.bc.ca with the username/password that was provided to you.
