import os

DEBUG = True

BIND = os.environ.get('BIND') or '0.0.0.0:8060'
APP_PORT = int(BIND.split(':')[1])
APP_HOST = BIND.split(':')[0]

NAMESPACE = os.environ.get('NameSpace') or 'http://mof.gov.ua/trembita/dict/wage'

USERID = os.environ.get('userId') or '0123456789'
TOKEN = os.environ.get('token') or 'bb96c2fc40d2d54617d6f276febe571f623a8dadf0b734855299b0e107fda32cf6b69f2da32b36445d73690b93cbd0f7bfc20e0f7f28553d2a4428f23b716e90'
