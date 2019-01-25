import requests
import json
from collections import defaultdict
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError

from requirements_documents.models import Section, Commodity, Heading, RequirementDocument, HasRequirementDocument, AbstractCommodity
# from requirements_documents.management.commands.scrape_section import get_and_update_commodity


COMMODITY_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/%s.json?currency=EUR&day=1&month=1&year=2019'


def get_heading_hierarchy(heading):

    if not heading.tts_obj.commodity_dicts:
        return

    # dicts_by_id = {
    #     (di['goods_nomenclature_sid'], di['leaf']): di
    #     for di in heading.tts_obj.commodity_dicts
    # }

    scrape_subtree(heading, heading.tts_obj.commodity_dicts, None)

    '''
    heading_leafs, to_remove = [], []
    for (code, is_leaf), di in dicts_by_id.items():
        if di['number_indents'] == 1 and is_leaf:
            heading_leafs.append(di)
            to_remove.append((code, is_leaf))
    for k in to_remove:
        del dicts_by_id[k]'''


def _create_commodity(di):
    obj, created = Commodity.objects.get_or_create(
        commodity_code=di['goods_nomenclature_item_id'],
        goods_nomenclature_sid=di['goods_nomenclature_sid'],
    )
    obj.tts_is_leaf = di['leaf']
    obj.tts_heading_json = di
    if created:
        obj.tts_json = get_commodity_json(obj.commodity_code)
    obj.save()
    return obj
    # heading_leaf_objects.append(obj)


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
            commodity_obj = _create_commodity(di)
            _attach_to_parent(commodity_obj, parent)
        else:
            abs_commodity_obj = _create_abstract_commodity(di)
            _attach_to_parent(abs_commodity_obj, parent)
            scrape_subtree(
                abs_commodity_obj, commodity_dicts, di['goods_nomenclature_sid']
            )


def _create_abstract_commodity(di):
    abs_commodity, _ = AbstractCommodity.objects.get_or_create(
        commodity_code=di['goods_nomenclature_item_id'],
        goods_nomenclature_sid=di['goods_nomenclature_sid'],
    )
    abs_commodity.tts_is_leaf = di['leaf']
    #abs_commodity.heading = heading
    abs_commodity.tts_heading_json = di
    abs_commodity.save()
    return abs_commodity


def _attach_to_parent(obj, parent):

    type_pair = type(obj), type(parent)

    if type_pair == (Commodity, Heading):
        obj.heading = parent
        obj.save()
    elif type_pair == (AbstractCommodity, Heading):
        obj.heading = parent
        obj.save()
    elif type_pair == (Commodity, AbstractCommodity):
        obj.parent_abstract_commodity = parent
        obj.save()
    elif type_pair == (AbstractCommodity, AbstractCommodity):
        obj.parent_abstract_commodity = parent
        obj.save()
    else:
        print('warning: cannot attach child %s to parent %s' % type_pair)



def get_heading_hierarchyOLD(heading):

    if not heading.tts_obj.commodity_dicts:
        return

    dicts_by_id = {
        # NOTE: this is different from 'goods_nomenclature_item_id'
        (di['goods_nomenclature_sid'], di['leaf']): di for di in heading.tts_obj.commodity_dicts
    }
    max_indents = 0
    for (code, is_leaf), di in dicts_by_id.items():
        if di['number_indents'] > max_indents:
            max_indents = di['number_indents']

    heading_leafs, to_remove = [], []
    for (code, is_leaf), di in dicts_by_id.items():
        if di['number_indents'] == 1 and is_leaf:
            heading_leafs.append(di)
            to_remove.append((code, is_leaf))
    for k in to_remove:
        del dicts_by_id[k]

    hierarchy = defaultdict(list)

    # do non-leafs first
    for (code1, is_leaf1), di1 in dicts_by_id.items():
        if is_leaf1:
            continue
        if code1 is None:
            import pdb; pdb.set_trace()
        for (code2, is_leaf2), di2 in dicts_by_id.items():
            if (code1, is_leaf1) == (code2, is_leaf2):
                continue
            if di2['parent_sid'] and di2['parent_sid'] == code1:
                hierarchy[(code1, is_leaf1)].append((code2, is_leaf2))
            elif di2['parent_sid'] is None and is_leaf2:
                import pdb; pdb.set_trace()  # should never get here
                print()

    import pdb; pdb.set_trace()

    for (code, is_leaf), children_keys in hierarchy.items():
        parent_di = dicts_by_id[(code, is_leaf)]
        if is_leaf:
            import pdb; pdb.set_trace()  # should never get here
        abs_commodity, _ = AbstractCommodity.objects.get_or_create(
            commodity_code=parent_di['goods_nomenclature_item_id'],
            goods_nomenclature_sid=parent_di['goods_nomenclature_sid'],
        )
        abs_commodity.tts_is_leaf = parent_di['leaf']
        abs_commodity.heading = heading
        abs_commodity.tts_heading_json = parent_di
        abs_commodity.save()

        for (code2, is_leaf2) in children_keys:
            child_di = dicts_by_id[(code2, is_leaf2)]
            assert is_leaf2 == child_di['leaf']
            assert child_di['parent_sid'] == parent_di['goods_nomenclature_sid']
            if is_leaf2:
                obj, created = Commodity.objects.get_or_create(
                    commodity_code=child_di['goods_nomenclature_item_id'],
                    goods_nomenclature_sid=child_di['goods_nomenclature_sid'],
                )
                obj.tts_is_leaf = child_di['leaf']
                obj.parent_abstract_commodity = abs_commodity
                #obj.heading = heading
                obj.goods_nomenclature_sid = child_di['goods_nomenclature_sid']
                obj.tts_heading_json = child_di
                if created:
                    obj.tts_json = get_commodity_json(obj.commodity_code)
                obj.save()
            else:
                obj, _ = AbstractCommodity.objects.get_or_create(
                    commodity_code=child_di['goods_nomenclature_item_id'],
                    goods_nomenclature_sid=child_di['goods_nomenclature_sid'],
                )
                obj.tts_is_leaf = child_di['leaf']
                obj.parent_abstract_commodity = abs_commodity
                obj.tts_heading_json = child_di
                obj.save()

    heading_leaf_objects = []
    for di in heading_leafs:
        obj, created = Commodity.objects.get_or_create(
            commodity_code=di['goods_nomenclature_item_id'],
            goods_nomenclature_sid=di['goods_nomenclature_sid'],
        )
        obj.tts_is_leaf = di['leaf']
        obj.heading = heading
        obj.tts_heading_json = di
        if created:
            obj.tts_json = get_commodity_json(obj.commodity_code)
        obj.save()
        heading_leaf_objects.append(obj)


def get_commodity_json(commodity_code):
    url = COMMODITY_URL % commodity_code
    print('\nstarting request: '+url)
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout:
        import pdb; pdb.set_trace()
        return None
    print('finished request')
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        print('url failed: ' + url)
        return None
    return json.loads(resp_content)


'''
@property
    def commodity_urls(self):
        return [((COMMODITY_URL % id), is_leaf) for (id, is_leaf) in self.commodity_ids]


#def get_and_update_commodity(commodity_url, is_leaf, heading_db_obj):


def infer_hierarchyOLD2(heading):
    dicts_by_id = {
        (di['goods_nomenclature_item_id'], di['leaf']): di for di in heading.tts_obj.commodity_dicts
    }
    max_indents = 0
    for (code, is_leaf), di in dicts_by_id.items():
        if di['number_indents'] > max_indents:
            max_indents = di['number_indents']

    heading_leafs, to_remove = [], []
    for (code, is_leaf), di in dicts_by_id.items():
        if di['number_indents'] == 1 and is_leaf:
            heading_leafs.append(di)
            to_remove.append((code, is_leaf))
    for k in to_remove:
        del dicts_by_id[k]

    non_leafs, leafs = [], []
    for (code, is_leaf), di in dicts_by_id.items():
        if is_leaf:
            leafs.append(di)
        else:
            non_leafs.append(di)

    hierarchy = defaultdict(list)

    for non_leaf_di in non_leafs:
        code1, is_leaf1 = non_leaf_di['goods_nomenclature_item_id'], non_leaf_di['leaf']
        for di2 in leafs + non_leafs:
            code2, is_leaf2 = di2['goods_nomenclature_item_id'], di2['leaf']
            if (code1, is_leaf1) == (code2, is_leaf2):
                continue
            if code1 == code2 or code2.startswith(code1.rstrip('0')):
                hierarchy[(code1, False)].append((code2, is_leaf2))

    for (code1, is_leaf1), child_keys in hierarchy.items():
        if is_leaf1:
            continue
        for (code2, is_leaf2) in child_keys:
            if is_leaf2:
                continue
            import pdb; pdb.set_trace()
            print()

    import pdb; pdb.set_trace()
    #
    # non_leafs = {}
    # for (code, is_leaf), di in dicts_by_id.items():
    #     if is_leaf is False:
    #         non_leafs[(code, is_leaf)] = []
    # import pdb; pdb.set_trace()


def infer_hierarchyOLD(heading):

    dicts_by_id = {
        (di['goods_nomenclature_item_id'], di['leaf']): di for di in heading.tts_obj.commodity_dicts
    }
    non_leafs = []
    for di in heading.tts_obj.commodity_dicts:
        id, is_leaf = di['goods_nomenclature_item_id'], di['leaf']

        if is_leaf is False:
            non_leafs.append(id)

    hierarchy = defaultdict(list)
    heading_leafs = []

    for di in heading.tts_obj.commodity_dicts:
        id, is_leaf = di['goods_nomenclature_item_id'], di['leaf']
        if is_leaf is True:
            parent_found = False
            for id2 in non_leafs:
                if id.startswith(id2.rstrip('0')):
                    parent_desc = id2 + ': ' + dicts_by_id[(id2, False)]['description']
                    child_desc = id + ': ' + dicts_by_id[(id, True)]['description']
                    hierarchy[parent_desc].append(child_desc)
                    parent_found = True
                    break
            if parent_found is False:
                heading_leafs.append(id + ': ' + dicts_by_id[(id, True)]['description'])

    pprint(heading_leafs)
    import pdb; pdb.set_trace()
'''


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):
        section_id = options['section_id']
        if section_id:
            headings = []
            section = Section.objects.get(section_id=section_id)
            for chapter in section.chapter_set.all():
                for heading in chapter.heading_set.all():
                    headings.append(heading)
        else:
            headings = Heading.objects.all()

        #headings = [Heading.objects.get(heading_code_4='0511')]

        for heading in headings:
            get_heading_hierarchy(heading)
