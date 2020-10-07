import logging
import json

from django_elasticsearch_dsl.search import Search
from elasticsearch_dsl.response.hit import Hit
from elasticsearch import Elasticsearch

from django.conf import settings

from hierarchy.models import NomenclatureTree

from search.documents.section import INDEX as section_index
from search.documents.chapter import INDEX as chapter_index
from search.documents.heading import INDEX as heading_index
from search.documents.subheading import INDEX as sub_heading_index
from search.documents.commodity import INDEX as commodity_index


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


indices = [section_index, chapter_index, heading_index, sub_heading_index, commodity_index]
alias_names = [idx._name for idx in indices]


def search_by_term(form_data=None):

    client = Elasticsearch(hosts=[settings.ES_URL])

    sort_object = {form_data.get("sort"): form_data.get("sort_order")}
    query_object = {
        "multi_match": {
            "query": form_data.get("q"),
            "type": "most_fields",
            "fields": ["keywords", "description"],
            "operator": "and" if "," not in form_data.get("q") else "or",
        }
    }

    request = (
        Search()
        .index(*alias_names)    # these are really alias names which is what we want to use
        .using(client)
        .query(query_object)
        .sort(sort_object)
    )

    filter_on_leaf = True if form_data.get("toggle_headings") == "1" else False

    if filter_on_leaf:
        request = request.filter("term", leaf=filter_on_leaf)

    start = (int(form_data.get("page")) - 1) * settings.RESULTS_PER_PAGE
    end = start + settings.RESULTS_PER_PAGE

    total_results = len(list(request.scan()))
    total_full_pages = int(total_results / settings.RESULTS_PER_PAGE)
    orphan_results = total_results % settings.RESULTS_PER_PAGE
    total = request.count()
    request = request[0:total]

    hits = request[start:end].execute()

    for hit in hits:
        try:
            hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
        except KeyError as exception:
            logger.info("{0} {1}".format(hit["commodity_code"], exception.args))

    page_range_start = start if start != 0 else start + 1
    page_range_end = (
        end if len(hits) == settings.RESULTS_PER_PAGE else start + len(hits)
    )
    total_pages = total_full_pages + 1 if orphan_results > 0 else total_full_pages

    return {
        "results": hits,
        "page_range_start": page_range_start,
        "page_range_end": page_range_end,
        "total_pages": total_pages,
        "total_results": total_results,
        "no_results": True if not total_results else False,
    }


def search_by_code(code):

    processed_query = process_commodity_code(code)
    query_object = {"term": {"commodity_code": processed_query}}

    client = Elasticsearch(hosts=[settings.ES_URL])
    hits = (
        Search()
        .index(*alias_names)
        .using(client)
        .query(query_object)
    )
    for hit in hits:
        try:
            hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
        except KeyError as exception:
            logger.info("{0} {1}".format(hit["commodity_code"], exception.args))
    return hits


def process_commodity_code(code):

    if len(code) == 1:
        code = "0" + code

    if code in ["00", "99"]:
        code = "9999"

    if len(code) == 4 and code[2:] == "00":
        code = code[:2]

    if len(code) == 6 and code[2:] == "0000":
        code = code[:2]

    if len(code) in [3, 5, 7, 9]:
        code = code[:-1]

    if len(code) < 10:

        if len(code) == 2:
            result = code + "00000000"
            return result

        if len(code) == 4:
            result = code + "000000"
            return result

        if len(code) == 6:
            result = code + "0000"
            return result

        if len(code) == 8:
            result = code + "00"
            return result

    elif len(code) > 10:
        result = code[:8] + "00"
        return result

    else:
        result = code
        return result


def get_alias_from_hit(hit: Hit) -> str:
    """The indexes are named (by our convention) in the form of {alias}-{datetime}.
    Given an ElasticSearch hit return the alias of index"""

    alias = hit.meta["index"].split("-")[0]
    return alias


def normalise_commodity_code(code: str) -> str:
    """
    Normalises a string which is a candidate for a commodity code.
    Removes all dots.

    """
    code = code.replace('.', '')
    return code
