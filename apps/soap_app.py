import json
import logging
from os import path

from spyne import String, Date, Decimal
from spyne import rpc, Application, ServiceBase, ComplexModel
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11

from apps.tools import *

logger = logging.getLogger('spyne')


class MinWage(ComplexModel):
    DateWage = Date(doc='Дата на яку потрібна мінімальна заробітна плата')
    WageMonth = Decimal(doc='')
    WageHour = Decimal(doc='')
    WageDateBegin = Date(doc='')
    WageDateEnd = Date(doc='')


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


class Get(ServiceBase):
    @rpc(
        Date(
            min_occurs=1,
            doc='Дата на яку потрібна мінімальна заробітна плата'
        ),
        _returns=MinWage)
    def GetMinWage(ctx, DateWage):
        mw = MinWage()
        mw.DateWage = DateWage
        for w in Wage:
            end = w.get('end') or datetime.date(2999, 12, 31)
            if w.get('start') <= DateWage <= end:
                mw.WageMonth = w.get('wage')
                mw.WageHour = w.get('wage_h')
                mw.WageDateBegin = w.get('start')
                mw.WageDateEnd = w.get('end')
        return mw


Get.event_manager.add_listener(
    'method_return_string', on_method_return_string
)


class Put(ServiceBase):

    @rpc(
        Date(min_occurs=1,
             doc='Дата з якої починается дія, формат (YYYY-MM-DD)'),
        Decimal(min_occurs=1, doc='Сума мінімальної заробітної плати'),
        Decimal(doc='Сума мінімальної погодинної заробітної плати'),
        _returns=String())
    def putMinWage(ctx, start, wage, wage_h):
        header = Header(ctx.in_document).get('Header')

        if header.get('userId') != ctx.udc.config.get('USERID'):
            return 'Вам не можно вносити зміни!'
        if not check(header.get('userId'), header.get('token')):
            return 'Вам не можно вносити зміни!!'
        if header.get('token') != ctx.udc.config.get('TOKEN'):
            return 'Вам не можно вносити зміни!!!'

        wage = float(str(wage))
        wage_h = float(str(wage_h))
        for w in Wage:
            if w.get('end'):
                continue
            if w.get('start') > start:
                return "Дата не может быть меньше"
            w.update({'end': start - datetime.timedelta(1)})

        Wage.append({
            'start': start, 'end': None,
            'wage': wage, 'wage_h': wage_h
        })

        with open('./data/Wage.json', 'w', encoding='utf-8') as f:
            json.dump(Wage, f, ensure_ascii=False,
                      indent=4, default=dtoc)

        return "OK"


Put.event_manager.add_listener(
    'method_return_string', on_method_return_string
)


def soap_put(flask_app):
    Sput = Application(
        [Put],
        tns='Directory.Minimum.Wage',
        name='PutMinWage',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sput.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sput


def soap_get(flask_app):
    Sget = Application(
        [Get],
        tns='Directory.Minimum.Wage',
        name='GetMinWage',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sget.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sget


def rest_get(flask_app):
    Sget = Application(
        [Get],
        tns='Directory.Minimum.Wage',
        name='GetMinWage',
        in_protocol=JsonDocument(validator='soft'),
        out_protocol=JsonDocument(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sget.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sget
