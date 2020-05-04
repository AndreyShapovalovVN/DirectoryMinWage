import logging

from spyne import rpc, Application, String
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11

from apps.tools import *

logger = logging.getLogger('spyne')

MinWage = MW.customize(min_occurs=1)
LWage = LW.customize(min_occurs=1)


class WageGet(XRoad):
    @rpc(
        Date(
            min_occurs=1,
            doc='Дата на яку потрібна мінімальна заробітна плата'
        ),
        _returns=MinWage)
    def GetMinWage(ctx, DateWage):
        Wage = read_dict('Wage.json')
        mw = MinWage()
        for w in Wage:
            end = w.get('end') or datetime.date(2999, 12, 31)
            if w.get('start') <= DateWage <= end:
                mw.MinWageMonth = w.get('wage')
                mw.MinWageHour = w.get('wage_h')
                mw.MinWageDateBegin = w.get('start')
                mw.MinWageDateEnd = end
        return mw

    @rpc(
        Date(
            min_occurs=1,
            doc='Дата на яку потрібн пржитковий мінімум'
        ),
        _returns=LWage)
    def GetLivingWage(ctx, DateWage):
        Wage = read_dict('LivingWage.json')
        lw = LWage()

        for w in Wage:
            end = w.get('end') or datetime.date(2999, 12, 31)
            if w.get('start') <= DateWage <= end:
                lw.LivingWage = w.get('LivingWage')
                lw.LivingWage6 = w.get('LivingWage6')
                lw.LivingWage18 = w.get('LivingWage18')
                lw.LivingWageEmployable = w.get('LivingWageEmployable')
                lw.LivingWageInvalid = w.get('LivingWageInvalid')
                lw.MinWageDateBegin = w.get('start')
                lw.MinWageDateEnd = end
        return lw


class WagePut(XRoad):

    @rpc(MinWage, _returns=String())
    def putMinWage(ctx, MinWage):
        header = Header(ctx.in_document).get('Header')

        if header.get('userId') != ctx.udc.config.get('USERID'):
            return 'Вам не можно вносити зміни!'
        if header.get('token') != ctx.udc.config.get('TOKEN'):
            return 'Вам не можно вносити зміни!!'

        Wage = read_dict('Wage.json')
        for w in Wage:
            if w.get('end'):
                continue
            if w.get('start') > MinWage.start:
                return "Дата початку не може бути меньш ніж %s" % w.get('start')
            w.update({'end': MinWage.start - datetime.timedelta(1)})

        Wage.append({
            'start': MinWage.start,
            'end': None,
            'wage': MinWage.wage,
            'wage_h': MinWage.wage_h
        })

        with open('./data/Wage.json', 'w', encoding='utf-8') as f:
            json.dump(Wage, f, ensure_ascii=False,
                      indent=4, default=dtoc)

        return "OK"

    @rpc(LWage, _returns=String())
    def putLivingWage(ctx, LivingWage):
        header = Header(ctx.in_document).get('Header')

        if header.get('userId') != ctx.udc.config.get('USERID'):
            return 'Вам не можно вносити зміни!'
        if header.get('token') != ctx.udc.config.get('TOKEN'):
            return 'Вам не можно вносити зміни!!'

        Wage = read_dict('LivingWage.json')
        for w in Wage:
            if w.get('end'):
                continue
            if w.get('start') > LivingWage.MinWageDateBegin:
                return "Дата початку не може бути меньш ніж %s" % w.get('start')
            w.update({
                'end': LivingWage.MinWageDateBegin - datetime.timedelta(1)
            })

        Wage.append({
            "start": LivingWage.MinWageDateBegin,
            "end": None,
            "LivingWage": LivingWage.LivingWage,
            "LivingWage6": LivingWage.LivingWage6,
            "LivingWage18": LivingWage.LivingWage18,
            "LivingWageEmployable": LivingWage.LivingWageEmployable,
            "LivingWageInvalid": LivingWage.LivingWageInvalid
        })

        with open('./data/LivingWage.json', 'w', encoding='utf-8') as f:
            json.dump(Wage, f, ensure_ascii=False,
                      indent=4, default=dtoc)

        return "OK"


def soap_put(flask_app):
    Sput = Application(
        [WagePut],
        tns='Directory.Wage',
        name='PutWage',
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
        [WageGet],
        tns='Directory.Minimum.Wage',
        name='GetWage',
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
        [WageGet],
        tns='Directory.Minimum.Wage',
        name='MinWage',
        in_protocol=HttpRpc(validator='soft'),
        out_protocol=JsonDocument(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sget.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sget
