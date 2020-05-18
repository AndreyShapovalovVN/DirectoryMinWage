import datetime
import hashlib
import json
from os import path

from spyne import Date, Float, ComplexModel

from settings import NAMESPACE


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
    __namespace__ = '%s/MinWage' % NAMESPACE
    MinWageMonth = Float(
        min_occurs=1, doc='Мінімальна заробітна плата'
    )
    MinWageHour = Float(
        min_occurs=1, doc='Мінімальна погодина заробітна плата'
    )
    Begin = Date(
        min_occurs=1, doc='Дата впровадження, формат (YYYY-MM-DD)'
    )
    End = Date(
        nullable=True, doc='Дата закінчення, формат (YYYY-MM-DD)'
    )


class LW(ComplexModel):
    __namespace__ = '%s/CostOfLiving' % NAMESPACE

    CostOfLiving = Float(
        min_occurs=1, doc='Загальний показник',
    )
    CostOfLiving6 = Float(
        min_occurs=1, doc='Діти до 6 років',
    )
    CostOfLiving18 = Float(
        min_occurs=1, doc='Діти від 6 до 18 років',
    )
    CostOfLivingEmployable = Float(
        min_occurs=1, doc='Працездатні особи',
    )
    CostOfLivingInvalid = Float(
        min_occurs=1, doc='Особи, що втратили працездатність',
    )
    Begin = Date(
        min_occurs=1, doc='Дата впровадження, формат (YYYY-MM-DD)'
    )
    End = Date(
        min_occurs=0, doc='Дата закінчення, формат (YYYY-MM-DD)'
    )
