# A Quickstart Guide to Setting Up eDivorce on MiniShift

These instructions assume you have 2 EMPTY projects created in MiniShift:

- jag-csb-edivorce-tools (BUILD)
- jag-csb-edivorce-dev (DEV)

For Minishift deployments we won't bother setting up Jenkins or NGINX.  


## Uploading Templates into OpenShift

1. Clone the project from Github, and then ```cd``` into the openshift/templates directory.

2. Log into the OpenShift console to get your command line token.  Then log into OpenShift from the command line.

3. Upload the templates into OpenShift with the following commands

    Tools templates
    ```
    oc create -f edivorce-build-template.yaml -n jag-csb-edivorce-tools
    ```

    Main eDivorce environment template
    ```
    oc create -f edivorce-environment-template.yaml -n jag-csb-edivorce-dev
    ```


## Setting up the Tools Project


###  Process the templates in the 'tools' project

#### These can be processed from the commandline
```
oc project jag-csb-edivorce-tools

oc process edivorce-build | oc create -f -
```

You can monitor the process of the build in the OpenShift console on Minishift.  You'll need to wait for it to finish before you can start the next step. 

## Setting up Dev

Tag the builds in the tools project so they can be deployed to dev
```
oc project jag-csb-edivorce-tools
```

Give the dev project access to Docker images stored in the tools project
```
oc project jag-csb-edivorce-dev
oc policy add-role-to-user system:image-puller system:serviceaccount:jag-csb-edivorce-dev:default -n jag-csb-edivorce-tools
oc policy add-role-to-user edit system:serviceaccount:jag-csb-edivorce-tools:default -n jag-csb-edivorce-dev
```

Deploy the Django app and the Postgresql DB (Read the section about "Important Configuration Options" above!)
```
oc process edivorce -v ENVIRONMENT_TYPE=minishift,PROXY_NETWORK=0.0.0.0/0  | oc create -f -
```

Edit the yaml for the edivorce-django deployment config through the web console

Find:

          kind: ImageStreamTag
          name: 'edivorce-django:deploy-to-dev'


Change to:

          kind: ImageStreamTag
          name: 'edivorce-django:latest'

Deploy Weasyprint
```
oc deploy weasyprint --latest
```

## Create a Route

Using the web console, create a new route called "minishift" in the jag-csb-edivorce-dev project.  The only thing you need to change is the name.  Otherwise just use default settings.  

## Log into eDivorce

You should be able to find your route in the edivorce-django deployment of the jag-csb-edivorce-dev project.  When you are prompted for a username and password you can use the password 'dovorce' with any username you choose.  

