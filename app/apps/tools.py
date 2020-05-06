import datetime
import hashlib
import json
from os import path

from spyne import Date, Float, ComplexModel


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


class UserDefinedContext(object):
    def __init__(self, flask_app):
        self.config = flask_app.config
        self.logger = flask_app.logger


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

    ProsperousMin = Float(
        min_occurs=1,
        doc='Загальний показник',
    )
    ProsperousMin6 = Float(
        min_occurs=1,
        doc='Діти до 6 років',
    )
    ProsperousMin18 = Float(
        min_occurs=1,
        doc='Діти від 6 до 18 років',
    )
    ProsperousMinEmployable = Float(
        min_occurs=1,
        doc='Працездатні особи',
    )
    ProsperousMinInvalid = Float(
        min_occurs=1,
        doc='Особи, що втратили працездатність',
    )
    MinWageDateBegin = Date(
        min_occurs=1,
        doc='Дата впровадження, формат (YYYY-MM-DD)'
    )
    MinWageDateEnd = Date(
        min_occurs=0,
        nullable=True,
        doc='Дата закінчення, формат (YYYY-MM-DD)')
