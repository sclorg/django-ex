# A Quickstart Guide to Setting Up eDivorce on OpenShift

## Before you get started
This project uses the scripts found in [openshift-developer-tools](https://github.com/BCDevOps/openshift-developer-tools) to setup and maintain OpenShift environments (both local and hosted).  Refer to the [OpenShift Scripts](https://github.com/BCDevOps/openshift-developer-tools/blob/master/bin/README.md) documentation for details.

These instructions assume:
* You have Git, Docker, and the OpenShift CLI installed on your system, and they are functioning correctly.  The recommended approach is to use either [Homebrew](https://brew.sh/) (MAC) or [Chocolatey](https://chocolatey.org/) (Windows) to install the required packages.
* You have followed the [OpenShift Scripts](https://github.com/BCDevOps/openshift-developer-tools/blob/master/bin/README.md) environment setup instructions to install and configure the scripts for use on your system.
* You have forked and cloned a local working copy of the project source code.
* You are using a reasonable shell.  A "reasonable shell" is obvious on Linux and Mac, and is assumed to be the git-bash shell on Windows.
* You are working from the top level `./openshift` directory for the project.

Good to have:
* A moderate to advanced knowledge of OpenShift. There are two good PDFs available from Red Hat and O'Reilly on [OpenShift for Developers](https://www.openshift.com/promotions/for-developers.html) and [DevOps with OpenShift](https://www.openshift.com/promotions/devops-with-openshift.html).

For the commands mentioned in these instructions, you can use the `-h` parameter for usage help and options information.

### Working with OpenShift

When working with openshift, commands are typically issued against the `server-project` pair to which you are currently connected.  Therefore, when you are working with multiple servers (local, and remote for instance) you should always be aware of your current context so you don't inadvertently issue a command against the wrong server and project.  Although you can login to more than one server at a time it's always a good idea to completely logout of one server before working on another.

The automation tools provided by `openshift-developer-tools` hide some of these details from you, in that they perform project context switching automatically.  However, what they don't do is provide server context switching.  They assume you are aware of your server context and you have logged into the correct server.

Some useful commands to help you determine your current context:
* `oc whoami -c` - Lists your current server and user context.
* `oc project` - Lists your current project context.
* `oc project [NAME]` - Switch to a different project context.
* `oc projects` - Lists the projects available to you on the current server.

## Setting up a local OpenShift environment

If you are NOT setting up a local OpenShift environment you can skip over this section, otherwise read on.

Setting up a local OpenShift environment is not much different than setting up a hosted environment, there are just a few extra steps and then you can follow the same instructions in either case.

The following procedure uses the `oc cluster up` approach to provision a OpenShift Cluster directly in Docker, but you could just as easily use MiniShift which can be installed using your preferred package manager (`Chocolatey` or `Homebrew`).

### Change into the top level openshift folder
```
cd /<PathToWorkingCopy>/openshift
```

### Provision a local OpenShift Cluster
```
oc-cluster-up.sh
```
This will start your local OpenShift cluster using persistence so your configuration is preserved across restarts.

*To cleanly shutdown your local cluster use `oc-cluster-down.sh`.*

**Login** to your local OpenShift instance on the command line and the Web Console, using `developer` as both the username and password.  To login to the cluster from the command line, you can get a login token from the Web Console: Login to the console.  From the **?** dropdown select **Command Line Tools**.  Click on the **Copy To Clipboard** icon next to the `oc login` line.

### Create a local set of OpenShift projects
```
generateLocalProjects.sh
```
**This command will only work on a local server context.  It will fail if you are logged into a remote server.**  This will generate four OpenShift projects; tools, dev, test, and prod.  The tools project is used for builds and DevOps activities, and dev, test, and prod are a set of deployment environments.

If you need (or want) to reset your local environments you can run `generateLocalProjects.sh -D` to delete all of the OpenShift projects.

### Finish Up

You now have a local OpenShift cluster with a set of projects that mirror what you would have in the hosted **Pathfinder** environment.

You can now configure these project exactly as you would your hosted environment with one minor difference.  You will need to fix the routes **after** you have run your deployment configurations.

Run the following script to create the default routes for your local environment:
```
updateRoutes.sh
```

### Local Override Options

When running locally your can override your build and deployment parameters by generating a set of local parameters.

To generate a set of local params, run;
```
genParams.sh -l
```
Local param files are ignored by Git, so you cannot accidentally commit them to the repository.

This allows you to do things like redirect your builds to use a different repository and/or branch.

To apply local settings while deploying your build and deployment configurations use the `-l` option with `genBuilds.sh` and `genDepls.sh`.

## 0. Build and publish the S2I image:

*TODO: Add this process to the build configurations...*

```docker build -t s2i-nginx git://github.com/BCDevOps/s2i-nginx```

### Tag and push this image to the OpenShift Docker Registry for your OpenShift Project:

```
docker tag s2i-nginx docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx

docker login docker-registry.pathfinder.gov.bc.ca -u <username> -p <token>

docker push docker-registry.pathfinder.gov.bc.ca/jag-csb-edivorce-tools/s2i-nginx
```

(your docker token is the same as your OpenShift login token)

## 1. Change into the top level openshift folder
```
cd /<PathToWorkingCopy>/openshift
```

## 2. Initialize the projects - add permissions and storage
```
initOSProjects.sh
```
This will initialize the projects with permissions that allow images from one project (tools) to be deployed into another project (dev, test, prod).  For production environments will also ensure the persistent storage services exist.

## 3. Generate the Build and Images in the "tools" project; Deploy Jenkins
```
genBuilds.sh
```
This will generate and deploy the build configurations into the `tools` project.  Follow the instructions written to the command line.

If the project contains any Jenkins pipelines a Jenkins instance will be deployed into the `tools` project automatically once the first pipeline is deployed by the scripts.  OpenShift will automatically wire the Jenkins pipelines to Jenkins projects within Jenkins.

Use `-h` to get advanced usage information.  Use the `-l` option to apply any local settings you have configured; when working with a local cluster you should always use the `-l` option.

### Updating Build and Image Configurations
If you are adding build and image configurations you can re-run this script.  You will encounter errors for any of the resources that already exist, but you can safely ignore these errors and allow the script to continue.

If you are updating build and image configurations use the `-u` option.

If you are adding and updating build and image configurations, run the script **without** the `-u` option first to create the new resources and then again **with** the `-u` option to update the existing configurations.

## 4. Generate the Deployment Configurations and Deploy the Components
```
genDepls.sh -e <EnvironmentName, one of [dev|test|prod]>
```
This will generate and deploy the deployment configurations into the selected project; `dev`, `test`, or `prod`.  Follow the instructions written to the command line.

Use `-h` to get advanced usage information.  Use the `-l` option to apply any local settings you have configured; when working with a local cluster you should always use the `-l` option.

### Important Configuration Settings

#### Mandatory Settings:

**PROXY_NETWORK**

While running `genDepls.sh` you will be prompted for the network address of the upstream proxy. This is used to ensure that requests come from the Justice Proxy only.  You will need to enter the address in IPV4 CIDR notation e.g. 10.10.15.10/16. The actual value you need to enter cannot be stored on Github because this would violate BC Government Github policies. The PROXY_NETWORK setting is currently the same for all 3 environments (dev, test, and prod)

An example of the [edivorce-django-deploy.overrides.sh](./edivorce-django-deploy.overrides.sh) script prompting for the value to use for PROXY_NETWORK;
```
Processing deployment configuration; templates/edivorce-django/edivorce-django-deploy.yaml ...
Loading parameter overrides for templates/edivorce-django/edivorce-django-deploy.yaml ...

Enter the network of the upstream proxy (in CIDR notation; for example 0.0.0.0/0); defaults to 0.0.0.0/0:

```

SITEMINDER_WHITE_LIST

While running `genDepls.sh` you will be prompted for a list of IP addresses that make up the white-list of hosts allowed to access the service.

The list must be provided as a space delimited list of IP addresses.

The actual values cannot be stored on Github because this would violate BC Government Github policies. The addresses are different for each environment (dev, test, and prod).

An example of the [nginx-proxy-deploy.overrides.sh](./nginx-proxy-deploy.overrides.sh) script prompting for the value to use for SITEMINDER_WHITE_LIST;
```
Processing deployment configuration; templates/nginx-proxy/nginx-proxy-deploy.yaml ...
Loading parameter overrides for templates/nginx-proxy/nginx-proxy-deploy.yaml ...

Enter the white list of trusted IP addresses that should be allowed to access the SiteMinder route (as a space delimited list of IP addresses):

```

This has the affect of adding the white-list to the `haproxy.router.openshift.io/ip_whitelist` element of the associated route configuration in the template [nginx-proxy-deploy.yaml](./templates/nginx-proxy/nginx-proxy-deploy.yaml)

The result looks something like this;

```
{
    "apiVersion": "v1",
    "kind": "Route",
    "metadata": {
        "annotations": {
            "haproxy.router.openshift.io/ip_whitelist": "1.1.1.1 2.2.2.2 3.3.3.3 4.4.4.4"
        },
        "labels": {
            "app": "nginx-proxy-siteminder-route",
            "template": "nginx-proxy-deployment-template"
        },
        "name": "nginx-proxy-siteminder-route"
    },
    "spec": {
        "host": "edivorce-dev.pathfinder.bcgov",
        "port": {
            "targetPort": "8080-tcp"
        },
        "to": {
            "kind": "Service",
            "name": "nginx-proxy",
            "weight": 100
        }
    }
},
```

Once deployed to OpenShift, the white-list can be viewed on the associated route's configuration page by clicking `Show Annotations`.
```
haproxy.router.openshift.io/ip_whitelist    1.1.1.1 2.2.2.2 3.3.3.3 4.4.4.4
```

The white-list can be updated manually by editing the associated route's yaml configuration directly.
```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: 1.1.1.1 2.2.2.2 3.3.3.3 4.4.4.4
...
```

#### Other Settings:

BASICAUTH_ENABLED

Turns on simple basic authentication for test and dev environments.  This setting is set to "True" in the dev and test environments only.

BASICAUTH_USERNAME / BASICAUTH_PASSWORD

Both the Username and Password will be randomly generated and can later be found by a project administrator in the Secrets section of the related OpenShift project.

### Updating Deployment Configurations

If you are adding deployment configurations you can re-run this script.  You will encounter errors for any of the resources that already exist, but you can safely ignore these errors and allow the script to continue.

If you are updating deployment configurations use the `-u` option.

If you are adding and updating deployment configurations, run the script **without** the `-u` option first to create the new resources and then again **with** the `-u` option to update the existing configurations.

**_Note;_**

**Some settings on some resources are immutable.  To replace these resources you will need to delete and recreate the associated resource(s).**

**Updating the deployment configurations can affect (overwrite) auto-generated secretes such as the database username and password.**

**Care must be taken with resources containing credentials or other auto-generated resources.  You must ensure such resources are replaced using the same values._**

## 5. Add Build Pipeline Webhook(s) to GitHub

1. Log into the web console ang go to the :"eDivorce App (build)" project

2. Select Builds => Pipelines => build-and-deploy-to-dev-pipeline => Configuration

3. Copy the GitHub wookhook URL

4. Go to the repository settings in Github, and add the webhook url under "Webhooks"

    - Payload URL = The URL you copied from OpenShift
    - Content type = application/json
    - Secret = Leave Blank
    - Just push the event
    - Active

# eDivorce Deployment Environments

There are three deployment environments set up for different purposes within OpenShift. They are available at the URLs below.

| Environment |  URL  | Justice URL |
| ----------- | ----- | ----------- |
| DEV | http://edivorce-dev.pathfinder.bcgov | https://dev.justice.gov.bc.ca/divorce |
| TEST | https://edivorce-test.pathfinder.bcgov | https://test.justice.gov.bc.ca/divorce |
| PROD | https://edivorce-prod.pathfinder.bcgov | https://justice.gov.bc.ca/divorce |

*Environments are typically only accessible through the associated Justice URL due to white-list applied to the pathfinder routes.*

These instructions assume you have 4 EMPTY projects created in OpenShift:

- jag-csb-edivorce-tools (BUILD)
- jag-csb-edivorce-dev (DEV)
- jag-csb-edivorce-test (TEST)
- jag-csb-edivorce-prod (PROD)

# How to Access OpenShift for eDivorce

## Web UI
- Login to https://console.pathfinder.gov.bc.ca:8443; you'll be prompted for GitHub authorization.  You must be part of the BCDevOps Github organization, and you must have access to the eDivorce projects.

## Command-line (```oc```) tools
- Copy command line login string from https://console.pathfinder.gov.bc.ca:8443/console/command-line.  It will look like ```oc login https://console.pathfinder.gov.bc.ca:8443 --token=xtyz123xtyz123xtyz123xtyz123```
- Paste the login string into a terminal session.  You are no authenticated against OpenShift and will be able to execute ```oc``` commands. ```oc -h``` provides a summary of available commands.

# Tips

## Data management operations

If you need to access the DB, you can either use the terminal window in the OpenShift console or the ```oc rsh```
command to get to the command line on the postgresql pod.

### You can find the current name of the postgresql pod in the web console

The pod identifiers change with every deployment, you need to find the current one

```
oc get pods | grep Running
```

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

## Logs

By default your Django application is served with gunicorn and configured to output its access log to stderr.
You can look at the combined stdout and stderr of a given pod with this command:

    oc get pods         # list all pods in your project
    oc logs <pod-name>

This can be useful to observe the correct functioning of your application.

## Debugging

If you are getting an "Internal Server Error" message on the test or prod environments, follow the steps below to enter debug mode.  

1. Use either use the terminal window in the OpenShift console or the ```oc rsh``` command to get to the command line on the postgresql pod.

```
vi edivorce/settings/openshift.py
```

at the very bottom of the file add the line:
```
DEBUG = True 
```

In order to load the new configuration you need to restart gunicorn.  But we can't restart gunicorn in the normal way because we don't have sudo access inside the openshift pod.  

type the command 

```
ps - x
```

You'll get a list of processes, and you need to find the correct PIDs

```
 PID TTY      STAT   TIME COMMAND                                                                                                                                                                                                                                                                                         
     1 ?        Ss     0:00 /opt/app-root/bin/python3 /opt/app-root/bin/gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config gunicorn_config.py                                                                                                                                                                    
   38 ?        S      0:02 /opt/app-root/bin/python3 /opt/app-root/bin/gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config gunicorn_config.py                                                                                                                                                                    
   39 ?        S      0:02 /opt/app-root/bin/python3 /opt/app-root/bin/gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config gunicorn_config.py                                                                                                                                                                    
   40 ?        S      0:02 /opt/app-root/bin/python3 /opt/app-root/bin/gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config gunicorn_config.py                                                                                                                                                                    
   41 ?        S      0:02 /opt/app-root/bin/python3 /opt/app-root/bin/gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config gunicorn_config.py                                                                                                                                                                    
   50 ?        Ss     0:00 /bin/sh                                                                                                                                 
```

Kill all the gunicorn processes EXCEPT #1.  #1 is the master process and it will restart the others for us

```
kill 38 39 40 41
```

Wait a 30 seconds type ps -x.  Ensuring that new PIDs have been created.  
Now you can see the yellow Django debug screen!!!

## Fixing a Postgres crash loop caused by a `tuple concurrently updated` error

If a Postgres database pod gets terminated unexpectedly it can trigger a crash loop with the following log signature.

```
pg_ctl: another server might be running; trying to start server anyway
waiting for server to start....LOG:  redirecting log output to logging collector process
HINT:  Future log output will appear in directory "pg_log".
..... done
server started
=> sourcing /usr/share/container-scripts/postgresql/start/set_passwords.sh ...
ERROR:  tuple concurrently updated
```

To fix the issue:
- Find the name of the postgres pod that is in the crash loop.
- Start an `oc debug` session with the pod.
- Scale the associated Postgres deployment to zero pods.
- From the cmd line of the debug session;
  - Run `run-postgresql`.  This is the `CMD` for the docker image.  As part of the start-up process the script creates a number of files that won't exist in the pod otherwise, namely `/var/lib/pgsql/openshift-custom-postgresql.conf` and `/var/lib/pgsql/passwd`, which will stop you from running any of the `pg_ctl` commands.  When you run the command you should see the same error output listed above.
  - Run `pg_ctl stop -D /var/lib/pgsql/data/userdata` to cleanly shutdown Postgres.  You should see;
    ```
    waiting for server to shut down.... done
    server stopped
    ```
  - Run `pg_ctl start -D /var/lib/pgsql/data/userdata` to start Postgres.  You should see the following output and it should wait there indefinitly (no errors);
    ```
    server starting
    sh-4.2$ LOG:  redirecting log output to logging collector process
    HINT:  Future log output will appear in directory "pg_log".
    ```
  - Press `enter` a couple of times to get back to the cmd prompt.
  - Run `pg_ctl stop -D /var/lib/pgsql/data/userdata`, and wait for postgres to stop.  This will ensure a clean shutdown.
    ```
    waiting for server to shut down.... done
    server stopped
    ```
  - Exit the debug session.
  - Scale the deployment to 1 pod.  Postgres should start normally now.

