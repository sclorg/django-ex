# eDivorce Environments

There are several environments set up for different purposes within OpenShift. They are available at the URLs below.

|Environment| URL |Justice URL|
|-----------|-----|-----|
|DEV|edivorce-dev.pathfinder.gov.bc.ca|justice.gov.bc.ca/divorce-dev|
|TEST|edivorce-test.pathfinder.gov.bc.ca|justice.gov.bc.ca/divorce-test|
|PROD|edivorce-prod.pathfinder.gov.bc.ca|justice.gov.bc.ca/divorce|


# How to access Jenkins for eDivorce

- Login to https://edivorce-jenkins.pathfinder.gov.bc.ca with the username/password that was provided to you.

# How to access OpenShift for eDivorce

## Web UI
- Login to https://console.pathfinder.gov.bc.ca:8443; you'll be prompted for GitHub authorization.  You must be part of the BCDevOps Github organization, and you must have access to the eDivorce projects.

## Command-line (```oc```) tools
- Download OpenShift [command line tools](https://github.com/openshift/origin/releases/download/v1.2.1/openshift-origin-client-tools-v1.2.1-5e723f6-mac.zip), unzip, and add ```oc``` to your PATH.
- Copy command line login string from https://console.pathfinder.gov.bc.ca:8443/console/command-line.  It will look like ```oc login https://console.pathfinder.gov.bc.ca:8443 --token=xtyz123xtyz123xtyz123xtyz123```
- Paste the login string into a terminal session.  You are no authenticated against OpenShift and will be able to execute ```oc``` commands. ```oc -h``` provides a summary of available commands.

# Project contents

- The "edivorce-tools" project contains the Jenkins instance and the other jsg-csb-edivorce-* projects contain different "environments".  The names are self-explanatory.


# Uploading Templates into OpenShift

1. Clone the project from Github, and then ```cd``` into the openshift/templates directory.

2. Log into the OpenShift Console to get your command line token.  Then log into OpenShift from the command line.

3. Upload the templates into OpenShift with the following commands (this can also be done via the web interface)

```
oc create -f ../jenkins/jenkins-pipeline-persistent-template.json -n jag-csb-edivorce-tools
oc create -f edivorce-build-template.yaml -n jag-csb-edivorce-tools
oc create -f nginx-build-template.yaml -n jag-csb-edivorce-tools
oc create -f ../jenkins/pipeline.yaml -n jag-csb-edivorce-tools

oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-dev
oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-test
oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-prod

oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-dev
oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-test
oc create -f nginx-environment-template.yaml -n jag-csb-edivorce-prod

```


# Setting up the Tools Project

Install Docker Toolbox on your computer

Open Docker QuickStart Terminal (need Docker engine started and env variables set) and build the S2I image:

```docker build -t s2i-nginx git://github.com/BCDevOps/s2i-nginx```

Tag and push this image to the OpenShift Docker Registry for your OpenShift Project:

```docker tag s2i-nginx docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx```

```docker login docker-registry.pathfinder.gov.bc.ca -u <username> -p <token>```

```docker push docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx```

(your docker token is the same as your OpenShift login token)


```
oc project jag-csb-edivorce-tools

oc process jenkins-pipeline-persistent | oc create -f -
oc process edivorce-build | oc create -f -
oc process nginx-build | oc create -f -

```

Select "Add to Project"

On the Browse Catalog tab, type "edivorce-build-pipeline" into the filter field.  Select the template. Create.
(For some reason this can't be done from the command line like the other templates)



# Setting up Dev/Test/Prod Projects

1. Give the dev/test/prod projects access to ImageStreams stored in the tools project

    ```
    oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-dev:default -n jag-csb-edivorce-tools
    oc policy add-role-to-user edit system:serviceaccount: jag-csb-edivorce-tools:default -n jag-csb-edivorce-dev

    oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-test:default -n jag-csb-edivorce-tools
    oc policy add-role-to-user edit system:serviceaccount: jag-csb-edivorce-tools:default -n jag-csb-edivorce-test

    oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-prod:default -n jag-csb-edivorce-tools
    oc policy add-role-to-user edit system:serviceaccount: jag-csb-edivorce-tools:default -n jag-csb-edivorce-prod
    ```

2. In the web console, go into the project you want to configure

3. Select "Add to Project"

4. On the Browse Catalog tab, type "edivorce" into the filter field.  Select the edivorce template.

    You need to enter values for the following fields:
    ```
        Type of environnment (dev,test or prod).
            - Type the word dev, test, or prod

        Network of upstream proxy
            - This is used to ensure that requests come from the Justice Proxy only. It
              should be entered in IPV4 CIDR notation e.g. 10.10.15.10/16. (The actual
              value you need to enter cannot be stored on Github because this would
              violate BC Government Github policies. However the PROXY_NETWORK setting
              is currently the same for all 3 environemts [dev/test/prod] )
    ```

5. Select "Add to Project" again

6. On the Browse Catalog tab, type "nginx" into the filter field.  Select the nginx template

    You need to enter values for the following fields:

    ```
        Type of environnment (dev,test or prod).
            - Type the word dev, test, or prod
    ```

7. Weasyprint doesn't deploy itself by default. (outstanding issue).  Go to Applications => Deployments => weasyprint and press the 'Deploy' button.


# Data management operations

You can either use the terminal window in the OpenShift console or the ```oc rsh``` command to get to the command line on the postgresql pod.

```
oc rsh postgresql-2-qp0oh

psql -d default

\dt

\q
```
 ** the pod identifiers change regularly, you need to find the current one
