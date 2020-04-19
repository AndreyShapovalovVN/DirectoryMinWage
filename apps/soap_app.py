import logging

from spyne import String, Date, Decimal
from spyne import rpc, Application, ServiceBase, ComplexModel
from spyne.protocol.json import JsonDocument
from spyne.protocol.http import HttpRpc
from spyne.protocol.soap import Soap11

from apps.tools import *

logger = logging.getLogger('spyne')


class MinWage(ComplexModel):
    __namespace__ = 'Directory.Minimum.Wage'

    MinWageMonth = Decimal(doc='Мінімальна заробітна плата')
    MinWageHour = Decimal(doc='Мінімальна погодина заробітна плата')
    MinWageDateBegin = Date(doc='Дата впровадження')
    MinWageDateEnd = Date(doc='Дата закінчення')


class Get(ServiceBase):
    @rpc(
        Date(
            min_occurs=1,
            doc='Дата на яку потрібна мінімальна заробітна плата'
        ),
        _returns=MinWage)
    def GetMinWage(ctx, DateWage):
        Wage = read_dict()
        mw = MinWage()
        for w in Wage:
            end = w.get('end') or datetime.date(2999, 12, 31)
            if w.get('start') <= DateWage <= end:
                mw.MinWageMonth = w.get('wage')
                mw.MinWageHour = w.get('wage_h')
                mw.MinWageDateBegin = w.get('start')
                mw.MinWageDateEnd = w.get('end')
        return mw


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

        Wage = read_dict()
        wage = float(str(wage))
        wage_h = float(str(wage_h))
        for w in Wage:
            if w.get('end'):
                continue
            if w.get('start') > start:
                return "Дата початку не може бути меньш ніж %s" % w.get('start')
            w.update({'end': start - datetime.timedelta(1)})

        Wage.append({
            'start': start, 'end': None,
            'wage': wage, 'wage_h': wage_h
        })

        with open('./data/Wage.json', 'w', encoding='utf-8') as f:
            json.dump(Wage, f, ensure_ascii=False,
                      indent=4, default=dtoc)

        return "OK"


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
    Put.event_manager.add_listener(
        'method_return_string', on_method_return_string
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
    Get.event_manager.add_listener(
        'method_return_string', on_method_return_string
    )
    return Sget


def rest_get(flask_app):
    Sget = Application(
        [Get],
        tns='Directory.Minimum.Wage',
        name='GetMinWage',
        in_protocol=HttpRpc(validator='soft'),
        out_protocol=JsonDocument(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sget.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sget
