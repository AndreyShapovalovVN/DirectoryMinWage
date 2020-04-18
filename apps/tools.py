import datetime
import re
import hashlib


def check(*args):
    h = hashlib.sha512(args[0].encode()).hexdigest()
    return h == args[1]


def ctod(date):
    try:
        dat = datetime.datetime.strptime(date, '%Y-%m-%d')
    except Exception:
        dat = None
    else:
        dat = dat.date()
    return dat


def dtoc(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__str__()


def on_method_return_string(ctx):
    ctx.out_string[0] = ctx.out_string[0].replace(b'soap11env', b'soapenv')


class UserDefinedContext(object):
    def __init__(self, flask_app):
        self.config = flask_app.config
        self.logger = flask_app.logger


def Header(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = Header(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret
