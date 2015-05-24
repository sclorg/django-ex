# Openshift Django quickstart

This project is meant to be forked and used to quickly deploy a Django web application to an [OpenShift](https://github.com/openshift/origin) cluster.
It assumes you have access to an existing OpenShift installation.

You can use this as a starting point to build your own application.

## Getting started

1. (optional) Create and activate a [virtualenv](https://virtualenv.pypa.io/) (you may want to use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)).

2. Fork this repo and clone your fork:

    `git clone https://github.com/rhcarvalho/openshift-django-quickstart.git`

3. Install dependencies:

    `pip install -r requirements.txt`

4. Create a development database:

    `./manage.py migrate`

4. If everything is alright, you should be able to start the Django development server:

    `./manage.py runserver`

5. Open your browser and go to http://127.0.0.1:8000, you will be greeted with a welcome page.

## What has been done for you

This is a minimal Django 1.8 project. It was created with these steps:

1. Create a virtualenv
2. Manually install requirements
3. `pip freeze > requirements.txt`
4. `django-admin startproject PROJECT_NAME .`
3. Manually update `project/settings.py` to configure `SECRET_KEY`, `DATABASE` and `STATIC_ROOT` entries.
4. `./manage.py startapp openshift`, to create the welcome page's app

## Deploying to OpenShift

The file `application-template.json` contains an OpenShift application template that you can add you your OpenShift project with:

* `osc create -f application-template.json`

Now you can browse to your OpenShift web console and create a new app from the 'django-quickstart' template.
After adjusting your preferences (or accepting the defaults), your application will be built and deployed.

You will probably want to set the `GIT_REPOSITORY` parameter to point to your fork.
