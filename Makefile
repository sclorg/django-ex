.PHONY: test-openshift-pytest
test-openshift-pytest:
	cd tests && PYTHONPATH=$(CURDIR) python3.12 -m pytest -s -rA --showlocals -vv test_django*.py
