import os

import pytest
from pathlib import Path

from container_ci_suite.openshift import OpenShiftAPI

test_dir = Path(os.path.abspath(os.path.dirname(__file__)))

VERSION=os.getenv("SINGLE_VERSION")
if not VERSION:
    VERSION="3.11-ubi8"

class TestDjangoAppExTemplate:

    def setup_method(self):
        self.oc_api = OpenShiftAPI(pod_name_prefix="django-example")
        json_raw_file = self.oc_api.get_raw_url_for_json(
            container="s2i-python-container", dir="imagestreams", filename="python-rhel.json"
        )
        self.oc_api.import_is(path=json_raw_file, name="python")
        json_raw_file = self.oc_api.get_raw_url_for_json(
            container="postgresql-container", dir="imagestreams", filename="postgresql-rhel.json"
        )
        self.oc_api.import_is(path=json_raw_file, name="postgresql")

    def teardown_method(self):
        self.oc_api.delete_project()

    def test_template_inside_cluster(self):
        if VERSION == "3.11-ubi8" or VERSION == "3.11-ubi9":
            branch_to_test = "4.2.x"
        elif VERSION == "3.9-ubi9":
            branch_to_test = "2.2.x"
        else:
            branch_to_test = "master"
        expected_output = "Welcome to your Django application"
        template_json = self.oc_api.get_raw_url_for_json(
            container="django-ex", branch=branch_to_test, dir="openshift/templates", filename="django-postgresql-persistent.json"
        )
        assert self.oc_api.deploy_template(
            template=template_json, name_in_template="django-example", expected_output=expected_output,
            openshift_args=[
                f"SOURCE_REPOSITORY_REF={branch_to_test}",
                f"PYTHON_VERSION={VERSION}",
                "NAME=django-example",
                "POSTGRESQL_VERSION=12-el8"
            ]
        )
        assert self.oc_api.template_deployed(name_in_template="django-example")
        assert self.oc_api.check_response_inside_cluster(
            name_in_template="django-example", expected_output=expected_output
        )

    def test_template_by_request(self):
        if VERSION == "3.11-ubi8" or VERSION == "3.11-ubi9":
            branch_to_test = "4.2.x"
        elif VERSION == "3.9-ubi9":
            branch_to_test = "2.2.x"
        else:
            branch_to_test = "master"
        expected_output = "Welcome to your Django application"
        template_json = self.oc_api.get_raw_url_for_json(
            container="django-ex", branch=branch_to_test,  dir="openshift/templates", filename="django-postgresql-persistent.json"
        )
        assert self.oc_api.deploy_template(
            template=template_json, name_in_template="django-example", expected_output=expected_output,
            openshift_args=[
                f"SOURCE_REPOSITORY_REF={branch_to_test}",
                f"PYTHON_VERSION={VERSION}",
                "NAME=django-example",
                "POSTGRESQL_VERSION=12-el8"
            ]
        )
        assert self.oc_api.template_deployed(name_in_template="django-example")
        assert self.oc_api.check_response_outside_cluster(
            name_in_template="django-example", expected_output=expected_output
        )
