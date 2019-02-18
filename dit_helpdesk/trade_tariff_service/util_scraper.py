import json
import requests

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading


COMMODITY_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/%s.json?currency=EUR&day=1&month=1&year=2019'


def scrape_heading_hierarchy(heading):

    if not heading.tts_obj.commodity_dicts:
        return

    scrape_subtree(heading, heading.tts_obj.commodity_dicts, None)


def scrape_subtree(parent, commodity_dicts, parent_sid):

    if parent_sid is None:
        commodity_dicts_curr = [
            di for di in commodity_dicts if di['number_indents'] == 1
        ]
    else:
        commodity_dicts_curr = [
            di for di in commodity_dicts
            if di['parent_sid'] == parent_sid
        ]

    for di in commodity_dicts_curr:
        if di['leaf']:
            commodity_obj = get_or_create_commodity_w_dict(di)
            _attach_to_parent(commodity_obj, parent)
        else:
            abs_commodity_obj = get_or_create_subheading_w_dict(di)
            _attach_to_parent(abs_commodity_obj, parent)
            scrape_subtree(
                abs_commodity_obj, commodity_dicts, di['goods_nomenclature_sid']
            )


def get_or_create_commodity_w_dict(di):
    obj, created = Commodity.objects.get_or_create(
        commodity_code=di['goods_nomenclature_item_id'],
        goods_nomenclature_sid=di['goods_nomenclature_sid'],
    )
    obj.tts_is_leaf = di['leaf']
    obj.tts_heading_json = json.dumps(di)
    if created:
        obj.tts_json = get_commodity_json(obj.commodity_code)
    obj.save()
    return obj


def get_or_create_subheading_w_dict(di):
    abs_commodity, _ = SubHeading.objects.get_or_create(
        commodity_code=di['goods_nomenclature_item_id'],
        goods_nomenclature_sid=di['goods_nomenclature_sid'],
    )
    abs_commodity.tts_is_leaf = di['leaf']
    abs_commodity.tts_heading_json = json.dumps(di)
    abs_commodity.save()
    return abs_commodity


def _attach_to_parent(obj, parent):

    type_pair = type(obj), type(parent)

    if type_pair == (Commodity, Heading):
        obj.heading = parent
        obj.save()
    elif type_pair == (SubHeading, Heading):
        obj.heading = parent
        obj.save()
    elif type_pair == (Commodity, SubHeading):
        obj.parent_subheading = parent
        obj.save()
    elif type_pair == (SubHeading, SubHeading):
        obj.parent_subheading = parent
        obj.save()
    else:
        print('warning: cannot attach child %s to parent %s' % type_pair)


def get_commodity_json(commodity_code):
    url = COMMODITY_URL % commodity_code
    print('        COMMODITY: '+url)
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout:
        import pdb; pdb.set_trace()
        return None
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        print('url failed: ' + url)
        return None
    return resp_content