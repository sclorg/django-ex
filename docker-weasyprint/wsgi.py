#!/usr/bin/env python

import json
import logging

from flask import Flask, request, make_response
from weasyprint import HTML

app = Flask('pdf')

@app.route('/health')
def index():
    return 'ok'


@app.before_first_request
def setup_logging():
    logging.addLevelName(logging.DEBUG, "\033[1;36m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


@app.route('/')
def home():
    return '''
        <h1>PDF Generator</h1>
        <p>The following endpoints are available:</p>
        <ul>
            <li>POST to <code>/pdf?filename=myfile.pdf</code>. The body should
                contain html</li>
            <li>POST to <code>/multiple?filename=myfile.pdf</code>. The body
                should contain a JSON list of html strings. They will each
                be rendered and combined into a single pdf</li>
        </ul>
    '''


@app.route('/pdf', methods=['POST'])
def generate():
    name = request.args.get('filename', 'unnamed.pdf')
    app.logger.info('POST  /pdf?filename=%s' % name)
    html = HTML(string=request.data)
    pdf = html.write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=%s' % name
    app.logger.info(' ==> POST  /pdf?filename=%s  ok' % name)
    return response


@app.route('/multiple', methods=['POST'])
def multiple():
    name = request.args.get('filename', 'unnamed.pdf')
    app.logger.info('POST  /multiple?filename=%s' % name)
    htmls = json.loads(request.data.decode('utf-8'))
    documents = [HTML(string=html).render() for html in htmls]
    pdf = documents[0].copy([page for doc in documents for page in doc.pages]).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=%s' % name
    app.logger.info(' ==> POST  /multiple?filename=%s  ok' % name)
    return response


if __name__ == '__main__':
    app.run()
