#!/usr/bin/env python3
import logging

from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from apps.flasked import app
from apps.soap_app import soap_get, rest_get, logger

import lxml
import gunicorn

my_apps = {}

my_apps['/DictWage'] = WsgiApplication(
    soap_get(app))
my_apps['/api'] = WsgiApplication(
    rest_get(app))

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, my_apps)

llevel = logging.DEBUG if app.config.get('DEBUG') else logging.INFO

soap_hendler = logging.FileHandler('./logs/standart.log')
soap_hendler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s: %(message)s'
))

logger.setLevel(llevel)
logger.addHandler(soap_hendler)

app.logger.setLevel(llevel)
app.logger.addHandler(soap_hendler)

logging.getLogger('spyne.protocol.xml').setLevel(llevel)

if __name__ == '__main__':
    app.run(host='192.168.1.16', port=app.config.get('APP_PORT'), threaded=True)
