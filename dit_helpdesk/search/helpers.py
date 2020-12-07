import logging
import json
from collections import defaultdict

from typing import Union

from django_elasticsearch_dsl.search import Search
from elasticsearch_dsl.response.hit import Hit
from elasticsearch import Elasticsearch

from django.conf import settings

from commodities.models import Commodity
from hierarchy.models import (
    Heading,
    SubHeading,
    Chapter,
)

from search.documents.section import INDEX as section_index, alias_pattern as section_pattern
from search.documents.chapter import INDEX as chapter_index, alias_pattern as chapter_pattern
from search.documents.heading import INDEX as heading_index, alias_pattern as heading_pattern
from search.documents.subheading import (
    INDEX as sub_heading_index,
    alias_pattern as subheading_pattern
)
from search.documents.commodity import INDEX as commodity_index, alias_pattern as commodity_pattern


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


indices = [section_index, chapter_index, heading_index, sub_heading_index, commodity_index]
alias_names = [idx._name for idx in indices]
alias_patterns = (
    section_pattern, chapter_pattern, heading_pattern, subheading_pattern, commodity_pattern)


def get_aliases_by_region(region=settings.PRIMARY_REGION):
    return (pattern.format(region=region.lower()) for pattern in alias_patterns)


class HierarchyIntegrityError(Exception):
    pass


def _build_search_request(query, sort_key, sort_order, filter_on_leaf=None):
    client = Elasticsearch(hosts=[settings.ES_URL])

    sort_object = {sort_key: sort_order}
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
        .index(*get_aliases_by_region())
        .using(client)
        .query(query_object)
        .sort(sort_object)
    )

    if filter_on_leaf:
        request = request.filter("term", leaf=filter_on_leaf)

    return request


def _choose_max_score(prev_score, new_score):
    return max(prev_score, new_score)


def _accumulate_score(prev_score, new_score):
    return prev_score + new_score


def _no_score(prev_score, new_score):
    return 0


def group_hits_by_chapter_heading(hits, score_strategy=_no_score):

    hits_by_chapter_heading = defaultdict(lambda: defaultdict(list))
    chapter_scores = defaultdict(lambda: 0)
    heading_scores = defaultdict(lambda: 0)

    for hit in hits:
        commodity_code = hit["commodity_code"]
        score = hit.meta["score"]

        alias = get_alias_from_hit(hit)
        model_name = get_model_name_from_alias(alias)

        if model_name == 'section':
            continue

        if model_name == 'chapter':
            hits_by_chapter_heading[commodity_code] = defaultdict(list)
            chapter_scores[commodity_code] = score_strategy(chapter_scores[commodity_code], score)
            continue

        try:
            hierarchy_context = hit["hierarchy_context"]
            if isinstance(hierarchy_context, (bytes, str)):
                hit["hierarchy_context"] = json.loads(hierarchy_context)
        except KeyError as exception:
            logger.warning("%s has no hierarchy context: %s", commodity_code, exception.args)
            continue

        flattened_context = [
            item
            for item_list in hit["hierarchy_context"]
            for item in item_list
        ]

        chapter_data = next(item for item in flattened_context if item["type"] == "chapter")
        chapter_code = chapter_data["commodity_code"]

        try:
            heading_data = next(item for item in flattened_context if item["type"] == "heading")
            heading_code = heading_data["commodity_code"]
        except StopIteration as e:
            if model_name == 'heading':
                heading_code = commodity_code
            else:
                raise HierarchyIntegrityError(
                    f"Can't find parent heading for {commodity_code}") from e

        hits_by_chapter_heading[chapter_code][heading_code].append(hit)
        heading_scores[heading_code] = score_strategy(heading_scores[heading_code], score)
        chapter_scores[chapter_code] = score_strategy(chapter_scores[chapter_code], score)

    return hits_by_chapter_heading, chapter_scores, heading_scores


def search_by_term(form_data=None, page_size=None):

    request = _build_search_request(
        sort_key=form_data.get("sort"),
        sort_order=form_data.get("sort_order"),
        query=form_data.get("q"),
        filter_on_leaf=True if form_data.get("toggle_headings") == "1" else False
    )

    start = (int(form_data.get("page")) - 1) * settings.RESULTS_PER_PAGE
    page_size = page_size or settings.RESULTS_PER_PAGE
    end = start + page_size

    total_results = len(list(request.scan()))
    total_full_pages = int(total_results / settings.RESULTS_PER_PAGE)
    orphan_results = total_results % settings.RESULTS_PER_PAGE
    total = request.count()
    request = request[0:total]

    hits = request[start:end].execute()
    all_hits = request[0:total].execute()

    for hit in hits:
        try:
            hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
        except KeyError as exception:
            logger.info("{0} {1}".format(hit["commodity_code"], exception.args))

    page_range_start = start if start != 0 else start + 1
    page_range_end = (
        end if len(hits) == page_size else start + len(hits)
    )
    total_pages = total_full_pages + 1 if orphan_results > 0 else total_full_pages

    return {
        "results": hits,
        "_all_results": all_hits,
        "page_range_start": page_range_start,
        "page_range_end": page_range_end,
        "total_pages": total_pages,
        "total_results": total_results,
        "no_results": True if not total_results else False,
    }


def _sorted_dict_keys_by_values(d):
    sorted_tuples = sorted(d.items(), key=lambda tup: tup[1], reverse=True)
    return [k for k, v in sorted_tuples]


def group_search_by_term(form_data=None, page_size=None, hits=None):
    sort_key = form_data.get("sort")

    if not hits:
        request = _build_search_request(
            sort_key=sort_key,
            sort_order=form_data.get("sort_order"),
            query=form_data.get("q"),
            filter_on_leaf=True if form_data.get("toggle_headings") == "1" else False
        )

        total_results = len(list(request.scan()))
        total = request.count()
        request = request[0:total]
        hits = request.execute()
    else:
        total_results = len(hits)

    score_strategy = _no_score if sort_key == 'commodity_code' else _choose_max_score

    grouped_hits, chapter_scores, heading_scores = group_hits_by_chapter_heading(
        hits, score_strategy=score_strategy)
    group_chapters = grouped_hits.keys()

    group_headings = []
    for chapter_code, hits_by_heading in grouped_hits.items():
        group_headings.extend(hits_by_heading.keys())

    chapter_sort_order = group_chapters
    heading_sort_order = group_headings

    if sort_key == '_score':
        chapter_sort_order = _sorted_dict_keys_by_values(chapter_scores)
        heading_sort_order = _sorted_dict_keys_by_values(heading_scores)

    return {
        "grouped_hits": grouped_hits,
        "group_chapters": group_chapters,
        "group_headings": group_headings,
        "group_result_count": len(group_chapters) + len(group_headings),
        "chapter_sort_order": chapter_sort_order,
        "heading_sort_order": heading_sort_order,
        "hits": hits,
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

    alias_parts = hit.meta["index"].split("-")[:-1]
    alias = "-".join(alias_parts)
    return alias


def get_model_name_from_alias(alias) -> str:
    parts = alias.split("-")
    model_name = parts[0]

    return model_name


INDEX_TO_MODEL_CLASS_MAP = {
    "chapter": Chapter,
    "heading": Heading,
    "subheading": SubHeading,
    "commodity": Commodity,
}


class ObjectNotFoundFromHit(Exception):
    pass


def get_object_from_hit(hit: Hit) -> Union[Chapter, Heading, SubHeading, Commodity]:
    """Returns the commodity object related to a hit."""
    alias = get_alias_from_hit(hit)
    model_name = get_model_name_from_alias(alias)
    model_class = INDEX_TO_MODEL_CLASS_MAP[model_name]

    try:
        model = model_class.objects.get(
            goods_nomenclature_sid=hit.id,
            **{
                model_class.COMMODITY_CODE_FIELD: hit["commodity_code"],
            },
        )
    except model_class.DoesNotExist:
        raise ObjectNotFoundFromHit()

    return model


def normalise_commodity_code(code: str) -> str:
    """
    Normalises a string which is a candidate for a commodity code.
    Removes all dots.

    """
    code = code.replace('.', '')
    return code
