# Openshift quickstart: Django

This is a [Django](http://www.djangoproject.com) project that you can use as the starting point to develop your own and deploy it on an [OpenShift](https://github.com/openshift/origin) cluster.

It assumes you have access to an existing OpenShift installation.

## What has been done for you

This is a minimal Django 1.8 project. It was created with these steps:

1. Create a virtualenv
2. Manually install Django and other dependencies
3. `pip freeze > requirements.txt`
4. `django-admin startproject project .`
3. Update `project/settings.py` to configure `SECRET_KEY`, `DATABASE` and `STATIC_ROOT` entries
4. `./manage.py startapp welcome`, to create the welcome page's app

From this initial state you can:
* create new Django apps
* remove the `welcome` app
* rename the Django project
* update settings to suit your needs
* install more Python libraries and add them to the `requirements.txt` file


## Local development

To run this project in your development machine, follow these steps:

1. (optional) Create and activate a [virtualenv](https://virtualenv.pypa.io/) (you may want to use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)).

2. Fork this repo and clone your fork:

    `git clone https://github.com/openshift/django-ex.git`

3. Install dependencies:

    `pip install -r requirements.txt`

4. Create a development database:

    `./manage.py migrate`

4. If everything is alright, you should be able to start the Django development server:

    `./manage.py runserver`

5. Open your browser and go to http://127.0.0.1:8000, you will be greeted with a welcome page.


## Deploying to OpenShift

To follow the next steps, you need to be logged in to an OpenShift cluster and have an OpenShift project where you can work on.

The directory `openshift/` contains OpenShift application template files that you can add you your OpenShift project with:

    osc create -f openshift/<TEMPLATE_NAME>.json

Now you can go to your OpenShift web console and create a new app from one of the templates that you have just added.
After adjusting your preferences (or accepting the defaults), your application will be built and deployed.

You will probably want to set the `GIT_REPOSITORY` parameter to point to your fork.

Alternatively, you can use the command line to create your new app:

    osc new-app --template=<TEMPLATE_NAME> --param=GIT_REPOSITORY=...,...

In the web console, the overview tab shows you a service, by default called "web", that encapsulates all pods running your Django application. You can access your application by browsing to the service's IP address and port.


## Special files in this repository

Apart from the regular files created by Django (`project/*`, `welcome/*`, `manage.py`), this repository contains:

```
.sti/
└── bin/           - scripts used by source-to-image
    ├── assemble   - executed to produce a Docker image with your code and dependencies during build
    └── run        - executed to start your app during deployment

openshift/         - application templates for OpenShift

scripts/           - helper scripts to automate some tasks

gunicorn_conf.py   - configuration for the gunicorn HTTP server

requirements.txt   - list of dependencies
```


## Data persistence

You can deploy this application without a configured database in your OpenShift project, in which case Django will use a temporary SQLite database that will live inside your application's container, and persist only until you redeploy your application.

After each deploy you get a fresh, empty, SQLite database. That is fine for a first contact with OpenShift and perhaps Django, but sooner or later you will want to persist your data across deployments.

To do that, you should add a properly configured database server or ask your OpenShift administrator to add one for you. Then use `osc env` to update the `DATABASE_*` environment variables in your DeploymentConfig to match your database settings.

Redeploy your application to have your changes applied, and open the welcome page again to make sure your application is successfully connected to the database server.


## Looking for help

If you get stuck at some point, or think that this document needs further details or clarification, you can give feedback and look for help using the channels mentioned in [the OpenShift Origin repo](https://github.com/openshift/origin), or by filling an issue.


## License

This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to [CC0](http://creativecommons.org/publicdomain/zero/1.0/).
