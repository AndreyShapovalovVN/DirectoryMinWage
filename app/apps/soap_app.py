import logging

from lxml.etree import _Element
from spyne import rpc, Application, String, ServiceBase
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11
from spyne.util.etreeconv import *

from apps.tools import *

logger = logging.getLogger('spyne')

MinWage = MW.customize(min_occurs=1)
LWage = LW.customize(min_occurs=1)


class DictWage(ServiceBase):
    @rpc(
        Date(
            min_occurs=1,
            doc='Дата на яку потрібна мінімальна заробітна плата'
        ),
        _returns=MinWage)
    def GetMinWage(ctx, DateWage):
        if isinstance(ctx.in_document, _Element):
            header = root_etree_to_dict(
                etree_strip_namespaces(ctx.in_document)
            )['Envelope'][0]['Header'][0]
            ctx.udc.logger.info('Header: %s', header)

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
    def GetProsperousMin(ctx, DateWage):
        if isinstance(ctx.in_document, _Element):
            header = root_etree_to_dict(
                etree_strip_namespaces(ctx.in_document)
            )['Envelope'][0]['Header'][0]
            ctx.udc.logger.info('Header: %s', header)

        Wage = read_dict('ProsperousMin.json')
        lw = LWage()
        for w in Wage:
            end = w.get('end') or datetime.date(2999, 12, 31)
            if w.get('start') <= DateWage <= end:
                lw.ProsperousMin = w.get('ProsperousMin')
                lw.ProsperousMin6 = w.get('ProsperousMin6')
                lw.ProsperousMin18 = w.get('ProsperousMin18')
                lw.ProsperousMinEmployable = w.get('ProsperousMinEmployable')
                lw.ProsperousMinInvalid = w.get('ProsperousMinInvalid')
                lw.MinWageDateBegin = w.get('start')
                lw.MinWageDateEnd = end
        return lw

    @rpc(MinWage, _returns=String())
    def putMinWage(ctx, MinWage):
        header = None
        if isinstance(ctx.in_document, _Element):
            header = root_etree_to_dict(
                etree_strip_namespaces(ctx.in_document)
            )['Envelope'][0]['Header'][0]
            ctx.udc.logger.info('Header: %s', header)

        if not header:
            return 'Вам не можно вносити зміни'
        if header.get('userId')[0] != ctx.udc.config.get('USERID'):
            return 'Вам не можно вносити зміни!'
        if header.get('token')[0] != ctx.udc.config.get('TOKEN'):
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
    def putProsperousMin(ctx, ProsperousMin):
        header = None
        if isinstance(ctx.in_document, _Element):
            header = root_etree_to_dict(
                etree_strip_namespaces(ctx.in_document)
            )['Envelope'][0]['Header'][0]
            ctx.udc.logger.info('Header: %s', header)

        if not header:
            return 'Вам не можно вносити зміни'
        if header.get('userId')[0] != ctx.udc.config.get('USERID'):
            return 'Вам не можно вносити зміни!'
        if header.get('token')[0] != ctx.udc.config.get('TOKEN'):
            return 'Вам не можно вносити зміни!!'

        Wage = read_dict('ProsperousMin.json')
        for w in Wage:
            if w.get('end'):
                continue
            if w.get('start') > ProsperousMin.MinWageDateBegin:
                return "Дата початку не може бути меньш ніж %s" % w.get('start')
            w.update({
                'end': ProsperousMin.MinWageDateBegin - datetime.timedelta(1)
            })

        Wage.append({
            "start": ProsperousMin.MinWageDateBegin,
            "end": None,
            "ProsperousMin": ProsperousMin.ProsperousMin,
            "ProsperousMin6": ProsperousMin.ProsperousMin6,
            "ProsperousMin18": ProsperousMin.ProsperousMin18,
            "ProsperousMinEmployable": ProsperousMin.ProsperousMinEmployable,
            "ProsperousMinInvalid": ProsperousMin.ProsperousMinInvalid
        })

        with open('./data/ProsperousMin.json', 'w', encoding='utf-8') as f:
            json.dump(Wage, f, ensure_ascii=False,
                      indent=4, default=dtoc)

        return "OK"


def soap_get(flask_app):
    Sget = Application(
        [DictWage],
        tns='Directory.Minimum.Wage',
        name='DictWage',
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
        [DictWage],
        tns='Directory.Minimum.Wage',
        name='DictWage',
        in_protocol=HttpRpc(validator='soft'),
        out_protocol=JsonDocument(),
    )

    def _flask_config_context(ctx):
        ctx.udc = UserDefinedContext(flask_app)

    Sget.event_manager.add_listener(
        'method_call', _flask_config_context
    )

    return Sget
