# Openshift Django quickstart

This project is meant to be forked and used to quickly deploy a Django web application to an [OpenShift](https://github.com/openshift/origin) cluster.
It assumes you have access to an existing OpenShift installation.

You can use this as a starting point to build your own application.

## Getting started

1. (optional) Create and activate a [virtualenv](https://virtualenv.pypa.io/) (you may want to use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)).

2. Fork this repo and clone your fork:

    git clone https://github.com/rhcarvalho/openshift-django-quickstart.git

3. Install dependencies:

    pip install -r requirements.txt

4. If everything is alright, you should be able to start the Django development server:

    ./manage.py runserver

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

1. osc process -f application-template.json - | osc create -
deploy
see it running


## Next steps

### Add your own code

Add your own code, commit and redeploy.
hack (create app) & redeploy

### Add a database

Your OpenShift administrator should provide you ...
Change the configuration to point to your PostgreSQL database server.

### Scaling up

osc resize dc/web ...

### Web server logs

see gunicorn logs


## Not covered

- add application monitoring (newrelic)
- add error monitoring (rollbar)
