import logging
import json
import re

from django_elasticsearch_dsl.search import Search
from elasticsearch import Elasticsearch

from django.conf import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def search_by_term(
    query, page, sort_by="ranking", sort_order="desc", filter_on_leaf=False
):
    client = Elasticsearch(hosts=[settings.ES_URL])

    sort_object = {sort_by: {"order": sort_order}}
    query_object = {
        "multi_match": {
            "query": query,
            "type": "most_fields",
            "fields": ["keywords", "description"],
            "operator": "and" if "," not in query else "or",
        }
    }

    request = (
        Search()
        .using(client)
        .query(query_object)
        .sort(sort_object)
        .filter("term", leaf=filter_on_leaf)
    )

    start = (page - 1) * settings.RESULTS_PER_PAGE
    end = start + settings.RESULTS_PER_PAGE

    total_results = len(list(request.scan()))
    total_full_pages = int(total_results / settings.RESULTS_PER_PAGE)
    orphan_results = total_results % settings.RESULTS_PER_PAGE

    total = request.count()

    request = request[0:total]
    hits = request[start:end].execute()
    hits = remove_duplicate_commodity_hits(hits)
    for hit in hits:
        try:
            hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
        except KeyError as exception:
            logger.info("{0} {1}".format(hit["commodity_code"], exception.args))

    return {
        "results": hits,
        "page_range_start": start if start != 0 else start + 1,
        "page_range_end": end
        if len(hits) == settings.RESULTS_PER_PAGE
        else start + len(hits),
        "total_pages": total_full_pages + 1 if orphan_results > 0 else total_full_pages,
        "total_results": total_results,
    }


def search_by_code(code):
    processed_query = process_commodity_code(code)
    query_object = {"term": {"commodity_code": processed_query}}
    client = Elasticsearch(hosts=[settings.ES_URL])
    hits = Search().using(client).query(query_object)
    hits = remove_duplicate_commodity_hits(hits)
    for hit in hits:
        try:
            hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
        except KeyError as exception:
            logger.info("{0} {1}".format(hit["commodity_code"], exception.args))
    return hits


def remove_duplicate_commodity_hits(response):
    # filter out duplicate headings and subheadings from the results
    seen = set()
    results = []
    for hit in response:
        key = str(hit["commodity_code"]) + hit["description"]
        if key not in seen:
            results.append(hit)
            seen.add(key)
    return results


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
        print("code: ", code)
        result = code
        return result
