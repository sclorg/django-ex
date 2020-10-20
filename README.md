# eDivorce

This is a [Django](http://www.djangoproject.com) project forked from the [openshift/django-ex](https://github.com/openshift/django-ex) repository.

eDivorce was developed by the British Columbia Ministry of Justice to help self represented litigants fill out the paperwork for their divorce.  It replaces existing fillable PDF forms with a friendly web interface.

The steps in this document assume that you have access to an OpenShift deployment that you can deploy applications on.

## Local development

Prerequesites:
* Docker
* Docker Compose
* Python 3.8

To run this project in your development machine, follow these steps:

1. (optional) Create and activate a [virtualenv](https://virtualenv.pypa.io/) (you may want to use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)).

2. Clone this repo:

    `git clone https://github.com/bcgov/eDivorce.git`

3. Install dependencies:

    `pip3.8 install -r requirements.txt`

4. Create an environment settings file by copying `.env.example` to `.env` (`.env` will be ignored by Git)

5. Create a development database:

    `python3.8 ./manage.py migrate`

6. Load questions from fixtures:
  
    `python3.8 ./manage.py loaddata edivorce/fixtures/Question.json`

7. If everything is alright, you should be able to start the Django development server:

    `python3.8 ./manage.py runserver 0.0.0.0:8000`

8. Start up docker containers:

    `docker-compose up -d`

9. Log in to the Keycloak administration console on http://127.0.0.1:8081 as user=admin/password=admin. Under Manage Users, create yourself a test account.  Username, Email, First Name and Last Name fields are needed. Don't forget to set a password on the 'Credentials' tab.

10. Open your browser and go to http://127.0.0.1:8000, you will be greeted with the eDivorce homepage.  You can log in with the account you created in step 9. 

### SCSS Compilation

SASS compilation is now handled by the internal `django-sass-processor` package.
In local development, it compiles `*.scss` files it finds into the same directory
when they're loaded in the browser (thereafter it recompiles on load when it
detects changes by timestamp difference).  The file is collected into the
`staticfiles` directory during build, so doesn't add overhead in production.


## OpenShift deployment

See: `openshift/README.md`

## Data persistence

For local development a SQLite database will be used.  For OpenShift deployments data will be stored in a PostgreSQL database, with data files residing on a persistent volume.

## License

    Copyright 2017 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
