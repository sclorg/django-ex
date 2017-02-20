# docker-weasyprint

[![Build Status](https://travis-ci.org/aquavitae/docker-weasyprint.svg?branch=master)](https://travis-ci.org/aquavitae/docker-weasyprint)

[Weasyprint](http://weasyprint.org/) as a microservice in a docker image.

# Fork details

This is a temporary fork of https://github.com/aquavitae/docker-weasyprint
There is a bug in WeasyPrint that can only be fixed by upgrading the libcairo2 library to a version greater than 1.14.2
see: https://github.com/Kozea/WeasyPrint/issues/233

A pull request has been submitted to docker-weasyprint:
https://github.com/aquavitae/docker-weasyprint/pull/4


# Building the image

cd to the directory containing the Dockerfile

```
docker build . -t edivorce/weasyprint:latest
```

# Deploying the custom built image to OpenShift


```
docker tag edivorce/weasyprint docker-registry.pathfinder.gov.bc.ca/<tools project>/weasyprint

docker login docker-registry.pathfinder.gov.bc.ca -u <username> -p <token>

docker push docker-registry.pathfinder.gov.bc.ca/<tools project>/weasyprint
```

* <username> is your Github username!
* <token> is your OpenShift token, not your Gihub token!


# Local Usage

Run the docker image, exposing port 5005 (because 5001 doesn't work on a Mac)

```
docker run -d -p 5005:5001 edivorce/weasyprint
```

A `POST` to port `/pdf` on port 5001 with an html body with give a response containing a PDF. The filename may be set using a query parameter, e.g.:

```
curl -X POST -d @source.html http://127.0.0.1:5005/pdf?filename=result.pdf
```

This will use the file `source.html` and return a response with `Content-Type: application/pdf` and `Content-Disposition: inline; filename=result.pdf` headers.  The body of the response will be the PDF.

In addition `/health` is a health check endpoint and a `GET` returns 'ok'.
