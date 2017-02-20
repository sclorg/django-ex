# How to configure a CI/CD pipeline for eDivorce on OpenShift

- Create a project to house the Jenkins instance that will be responsible for promoting application images (via OpenShift ImageStreamTagS) across environment; the exact project name used was "edivorce".
- Create the BuildConfiguration within this project using the ```oc``` command and "edivorce-build-template.yaml" file in the templates directory:

```
oc process -f edivorce-build-template.yaml -v NAME=<product-name> -v SOURCE_REPOSITORY_URL=<github url> -v SOURCE_REPOSITORY_REF=<branch or ref> | oc create -f -
```

For example:

```
oc process -f edivorce-build-template.yaml -v NAME=edivorce-django -v SOURCE_REPOSITORY_URL=https://github.com/bcgov/eDivorce.git -v SOURCE_REPOSITORY_REF=master | oc create -f -
```



- Deploy a Jenkins instance with persistent storage into the edivorce project using the web gui
- Install the Promoted Builds Jenkins plugin
- Configure a job that has an OpenShift ImageStream Watcher as its SCM source and promotion states for each environment
- In each promotion configuration, tag the target build's image to the appropriate promotion level; this was done using a shell command because the OpenShift plugins do not appear to handle parameter subsitution inside promotions properly.
- Create an OpenShift project for each "environment" (e.g. DEV, TEST, PROD); Exact names used were jag-csb-edivorce-dev, jag-csb-edivorce-test, jag-csb-edivorce-prod
- Configure the access controls to allow the Jenkins instance to tag imagestreams in the environment projects, and to allow the environment projects to pull images from the eDivorce project:

```
oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-<env-name>:default -n jag-csb-edivorce-tools
oc policy add-role-to-user edit system:serviceaccount: jag-csb-edivorce-tools:default -n jag-csb-edivorce-<env-name>
```

- Use the YAML files in this directory  and `oc` tool to create the necessary resources within each project:

```
oc process -f edivorce-environment-template.yaml -v ENVIRONMENT_TYPE=<env-name> | oc create -f -
```

For example:

```
oc process -f edivorce-environment-template.yaml -v ENVIRONMENT_TYPE=dev,VOLUME_CAPACITY=1Gi | oc create -f -
```

# eDivorce Environments

There are several environments set up for different purposes within OpenShift. They are available at the URLs below.

|Environment| URL |Notes|
|-----------|-----|-----|
|DEV|edivorce-dev.pathfinder.gov.bc.ca| |
|TEST|edivorce-test.pathfinder.gov.bc.ca| |
|PROD|edivorce-prod.pathfinder.gov.bc.ca| |



# How to access Jenkins for eDivorce

- Login to https://edivorce-jenkins-edivorce.pathfinder.gov.bc.ca with the username/password that was provided to you.

# How to access OpenShift for eDivorce

## Web UI
- Login to https://console.pathfinder.gov.bc.ca:8443; you'll be prompted for GitHub authorization.

## Command-line (```oc```) tools
- Download OpenShift [command line tools](https://github.com/openshift/origin/releases/download/v1.2.1/openshift-origin-client-tools-v1.2.1-5e723f6-mac.zip), unzip, and add ```oc``` to your PATH.
- Copy command line login string from https://console.pathfinder.gov.bc.ca:8443/console/command-line.  It will look like ```oc login https://console.pathfinder.gov.bc.ca:8443 --token=xtyz123xtyz123xtyz123xtyz123```
- Paste the login string into a terminal session.  You are no authenticated against OpenShift and will be able to execute ```oc``` commands. ```oc -h``` provides a summary of available commands.

# Project contents

- The "edivorce-tools" project contains the Jenkins instance and the other jsg-csb-edivorce-* projects contain different "environments".  The names are self-explanatory.

# Data management operations

todo: add instructions on how to 'oc rsh' into the django pod to manage the postgresql pod

# Background reading/Resources

[Free OpenShift book](https://www.openshift.com/promotions/for-developers.html) from RedHat – good overview

[Red Hat Container Development Kit](http://developers.redhat.com/products/cdk/overview/)

OpenShift CI/CD pieline Demos:

- https://www.youtube.com/watch?v=65BnTLcDAJI
- https://www.youtube.com/watch?v=wSFyg6Etwx8




