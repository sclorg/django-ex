# Openshift quickstart: Django

This is a [Django](http://www.djangoproject.com) project that you can use as the starting point to develop your own and deploy it on an [OpenShift](https://github.com/openshift/origin) cluster.

It assumes you have access to an existing OpenShift installation.

## What has been done for you

This is a minimal Django 1.8 project. It was created with these steps:

1. Create a virtualenv
2. Manually install Django and other dependencies
3. `pip freeze > requirements.txt`
4. `django-admin startproject project .`
3. Manually update `project/settings.py` to configure `SECRET_KEY`, `DATABASE` and `STATIC_ROOT` entries.
4. `./manage.py startapp welcome`, to create the welcome page's app


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

[TODO]
