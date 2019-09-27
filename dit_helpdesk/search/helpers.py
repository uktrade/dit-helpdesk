import logging
import json
import re

from django_elasticsearch_dsl.search import Search
from elasticsearch import Elasticsearch

from django.conf import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def search(query, page):
    client = Elasticsearch(hosts=[settings.ES_URL])

    sort_object = {"ranking": {"order": "desc"}}
    query_object = {
        "multi_match": {
            "query": query,
            "type": "most_fields",
            "fields": ["keywords", "description"],
            "operator": "and" if "," not in query else "or"
        }
    }
    request = Search().using(client).query(query_object).sort(sort_object)

    start = (page - 1) * settings.RESULTS_PER_PAGE
    end = start + settings.RESULTS_PER_PAGE

    total_results = len(list(request.scan()))
    total_full_pages = int(total_results / settings.RESULTS_PER_PAGE)
    orphan_results = total_results % settings.RESULTS_PER_PAGE

    total = request.count()

    request = request[0:total]
    response = request[start:end].execute()

    # filter out duplicate headings and subheadings from the results
    seen = []
    results = []

    for hit in response:
        if (hit["commodity_code"], hit["description"]) not in seen:
            try:
                hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
            except KeyError as exception:
                logger.info("{0} {1}".format(hit["commodity_code_html"] , exception.args))
            results.append(hit)
        seen.append((hit["commodity_code"], hit["description"]))
    return {
        "results": results,
        "page_range_start": start if start != 0 else start + 1,
        "page_range_end": end if len(results) == settings.RESULTS_PER_PAGE else start + len(results),
        "total_pages": total_full_pages + 1 if orphan_results > 0 else total_full_pages,
        'total_results': total_results,
    }
