import datetime
import hashlib
import json
import re
from os import path


def read_dict():
    if path.isfile('./data/Wage.json'):
        Wage = []
        with open('./data/Wage.json', 'r', encoding='utf-8') as f:
            w = json.load(f)
        for l in w:
            Wage.append(
                {
                    'start': ctod(l.get('start')),
                    'end': ctod(l.get('end')),
                    'wage': l.get('wage'),
                    'wage_h': l.get('wage_h'),
                }
            )
    else:
        Wage = []

    return Wage


def check(*args):
    return hashlib.sha512(args[0].encode()).hexdigest() == args[1]


def ctod(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    return date


def dtoc(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__str__()


def on_method_return_string(ctx):
    if isinstance(ctx.out_string, list):
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
