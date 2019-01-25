import json
from multiprocessing.pool import ThreadPool
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from psqlextra.query import ConflictAction
import requests

from requirements_documents.models import Section, Commodity, RequirementDocument, HasRequirementDocument
from requirements_documents.util import mclean, fhtml

# NOTE: the destinationCountry is 'GB' in one and 'eu' in the other
REQUIREMENTS_URL = "https://trade.ec.europa.eu/services/reqs/public/v1//requirements?destinationCountry=%(destination_country)s&originCountry=%(origin_country)s&product=%(commodity)s&lang=%(language)s"
REQUIREMENT_URL = "https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=%(destination_country)s&lang=%(language)s&code=%(code)s&reqType=%(requirement_type)s"


HASREQ_CREATION_DICT_FIELDS = [
    'commodity_pk', 'document_id_key',
    'eu_trade_helpdesk_website_origin_country',
    'eu_trade_helpdesk_website_destination_country',
]

'''

commodity:0207449100
-------------------------

-Import Proceedures:

  "EU import procedures"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=overview&reqType=o

  "Documents for customs and clearance"
designated webpage:  http://trade.ec.europa.eu/tradehelp/documents-customs-clearance

  "Import procedures and competent authorities for: United Kingdom"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=overview&reqType=o



-Product Requirements:


clicking link calls JS function:  openRequirementWindow(requirement.code, requirement.type)
todo: check how the results match up with:   "https://trade.ec.europa.eu/services/reqs/public/v1//requirements?destinationCountry=GB&originCountry=" + country + "&product=" + commodity[:8] + "&lang=EN"
 
  "Control of contaminants in foodstuffs"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heafocon&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heafocon&reqType=s

  "Control of pesticide residues in plant and animal products intended for human consumption"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heapestires&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heapestires&reqType=s

  "Control of residues of veterinary medicines in animals and animal products for human consumption"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heaveteres&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heaveteres&reqType=s

  "Health control of Genetically Modified (GM) food and novel food"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heagmonf&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heagmonf&reqType=s

  "Health control of products of animal origin for human consumption"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heaahc&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heaahc&reqType=s

  "Health control of products of animal origin not intended for human consumption"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heaanhc&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heaanhc&reqType=s

  "Traceability, compliance and responsibility in food and feed"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=safefood&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=safefood&reqType=s

  "Labelling of foodstuffs"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=lblfood&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=lblfood&reqType=s  
  
  
  "Marketing standards for poultry meat"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=mktpoult&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=mktpoult&reqType=s

  "Voluntary - Products from organic production"
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=sporgan&reqType=s
https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=sporgan&reqType=s


'''

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):
        section_id = options['section_id']
        if section_id is None:
            exit('<section_id> argument expected')

        get_documents(section_id)


def get_section_commodities(section_id):
    commodities = []
    section = Section.objects.get(section_id=section_id)
    for chapter in section.chapter_set.all():
        for heading in chapter.heading_set.all():
            for commodity in heading.commodity_set.all():
                commodities.append(commodity)
    return commodities


def get_documents(section_id):

    commodities = get_section_commodities(section_id)

    pool = ThreadPool(25)
    results = []
    for country in settings.TTS_COUNTRIES:
        for commodity_obj in commodities:
            # get_has_requirement_document_creation_dicts(commodity_obj, country)
            # continue
            res = pool.apply_async(
                get_hasreq_creation_dicts,
                args=(commodity_obj, country)  # 'EN'
            )
            results.append(res)
        time.sleep(10)  # no need to rush creating tasks!
    print('waiting for threads to finish')
    pool.close()
    pool.join()

    document_dicts, hasreq_dicts = [], []
    for res in results:
        res = res.get()
        document_dicts.extend(res[0])
        hasreq_dicts.extend(res[1])

    assert len(document_dicts) == len(hasreq_dicts)

    print('creating objects')
    create_db_objects(document_dicts, hasreq_dicts)
    print('finished')


def copy_dict(d, without=None):
    new_d = d.copy()
    for key in (without or []):
        if key in new_d:
            new_d.pop(key)
    return new_d


def bulk_upsert_documents(document_dicts):

    def document_keys(di):
        keys, values = [], []
        for k in RequirementDocument.UNIQUENESS_FIELDS:
            keys.append(k)
            values.append(di[k])
        return tuple(keys), tuple(values)

    doc_dicts_unique = {document_keys(di)[1]: di for di in document_dicts}
    doc_dicts_unique = [di for di in doc_dicts_unique.values()]

    results = (
        RequirementDocument.pg_objects
        .on_conflict(RequirementDocument.UNIQUENESS_FIELDS, ConflictAction.UPDATE).bulk_upsert(
            conflict_target=RequirementDocument.UNIQUENESS_FIELDS,
            rows=doc_dicts_unique
        )
    )
    return results


def bulk_upsert_hasreqs(hasreq_dicts, document_objects):

    # make unique
    hasreq_dicts = {di['id_key']: di for di in hasreq_dicts}
    hasreq_dicts = [v for v in hasreq_dicts.values()]

    commodity_pks = [di['commodity_pk'] for di in hasreq_dicts]
    commodity_pks = [v for v in set(commodity_pks)]
    commodity_objects = Commodity.objects.filter(pk__in=commodity_pks)

    commodities_by_pk = {o.pk: o for o in commodity_objects}
    documents_by_id_key = {o.get_id_key(): o for o in document_objects}
    for di in hasreq_dicts:
        di['document'] = documents_by_id_key[di['document_id_key']]
        di['commodity'] = commodities_by_pk[di['commodity_pk']]
        del di['document_id_key']
        del di['commodity_pk']
        del di['id_key']

    results = (
        HasRequirementDocument.pg_objects
        .on_conflict(HasRequirementDocument.UNIQUENESS_FIELDS, ConflictAction.UPDATE).bulk_upsert(
            conflict_target=HasRequirementDocument.UNIQUENESS_FIELDS,
            rows=hasreq_dicts
        )
    )
    return results


def create_db_objects(document_dicts, hasreq_dicts):
    """
    Create RequirementDocument and HasRequirementDocument objects
    """
    # creates/updates the documents and returns dictionaries with 'id'
    document_dicts = bulk_upsert_documents(document_dicts)

    document_objects = RequirementDocument.objects.filter(
        id__in=[di['id'] for di in document_dicts]
    )

    hasreq_objects = bulk_upsert_hasreqs(hasreq_dicts, document_objects)

    return document_objects, hasreq_objects


def get_hasreq_creation_dicts(commodity_obj, country, language='EN'):

    url = REQUIREMENTS_URL % {
        'origin_country': country, 'commodity': commodity_obj.commodity_code,
        'language': language, 'destination_country': 'GB'
    }

    document_creation_dicts = []
    has_req_document_creation_dicts = []

    response = requests.get(url)
    data = json.loads(response.content)

    for item in data:
        code = mclean(item["code"])
        label = mclean(item["label"])
        requirement_type = mclean(item["type"])

        document_dict, doc_id_key = get_commodity_document_dict(
            code, requirement_type
        )
        if document_dict is None:
            continue

        document_creation_dicts.append(document_dict)
        has_req_dict = {
            'commodity_pk': commodity_obj.pk,
            'document_id_key': doc_id_key,
            'eu_trade_helpdesk_website_destination_country': 'GB',
            'eu_trade_helpdesk_website_origin_country': country,
            'eu_trade_helpdesk_website_label': label,
        }
        has_req_dict['id_key'] = tuple([  # will be used below to remove duplicates
            has_req_dict[k] for k in HASREQ_CREATION_DICT_FIELDS
        ])
        has_req_document_creation_dicts.append(has_req_dict)

    return document_creation_dicts, has_req_document_creation_dicts


def get_commodity_document_dict(
        code, requirement_type, destination_country='eu', language='en'
):
    url = REQUIREMENT_URL % {
        'destination_country': destination_country, 'language': language,
        'code': code, 'requirement_type': requirement_type
    }
    response = requests.get(url)
    if response.status_code != 200:
        print('warning: %s gave status: %s' % (url, response.status_code))
        return None

    html = response.text

    dictionary = {
        'code': code, 'requirement_type': requirement_type,
        'destination_country': destination_country, 'language': language,
        'html': html, 'html_normalised': fhtml(html), 'query_url': url,
    }
    id_key = tuple([
        dictionary[k] for k in RequirementDocument.UNIQUENESS_FIELDS
    ])
    return dictionary, id_key
