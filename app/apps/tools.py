import datetime
import hashlib
import json
import re
from os import path

from spyne import Date, Float, ComplexModel
from spyne import ServiceBase


def read_dict(data):
    if path.isfile(path.join('./data', data)):
        Wage = []
        with open(path.join('./data', data), 'r', encoding='utf-8') as f:
            w = json.load(f)
        for l in w:
            l.update(
                {
                    'start': ctod(l.get('start')),
                    'end': ctod(l.get('end')),
                }
            )
            Wage.append(l)
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
        ctx.out_string[0] = ctx.out_string[0].replace(b'soap12env', b'soapenv')


class XRoad(ServiceBase):
    pass


XRoad.event_manager.add_listener(
    'method_return_string', on_method_return_string
)


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

class MW(ComplexModel):
    __namespace__ = 'Directory.Minimum.Wage'
    MinWageMonth = Float(
        min_occurs=1,
        doc='Мінімальна заробітна плата'
    )
    MinWageHour = Float(
        min_occurs=1,
        doc='Мінімальна погодина заробітна плата'
    )
    MinWageDateBegin = Date(
        min_occurs=1,
        doc='Дата впровадження, формат (YYYY-MM-DD)'
    )
    MinWageDateEnd = Date(
        nullable=True,
        doc='Дата закінчення, формат (YYYY-MM-DD)'
    )


class LW(ComplexModel):
    __namespace__ = 'Directory.Minimum.Living'

    LivingWage = Float(
        min_occurs=1
    )
    LivingWage6 = Float(
        min_occurs=1
    )
    LivingWage18 = Float(
        min_occurs=1
    )
    LivingWageEmployable = Float(
        min_occurs=1
    )
    LivingWageInvalid = Float(
        min_occurs=1
    )
    MinWageDateBegin = Date(
        min_occurs=1,
        doc='Дата впровадження, формат (YYYY-MM-DD)'
    )
    MinWageDateEnd = Date(
        min_occurs=0,
        nullable=True,
        doc='Дата закінчення, формат (YYYY-MM-DD)')
