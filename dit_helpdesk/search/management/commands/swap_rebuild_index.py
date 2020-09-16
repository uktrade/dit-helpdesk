import datetime as dt
import logging

from django.core.management.base import BaseCommand

from elasticsearch_dsl import connections

from search.documents.section import SectionDocument, INDEX as section_index
from search.documents.chapter import ChapterDocument, INDEX as chapter_index
from search.documents.heading import HeadingDocument, INDEX as heading_index
from search.documents.subheading import SubHeadingDocument, INDEX as sub_heading_index
from search.documents.commodity import CommodityDocument, INDEX as commodity_index


logger = logging.getLogger(__name__)


indices = {
    SectionDocument: section_index,
    ChapterDocument: chapter_index,
    HeadingDocument: heading_index,
    SubHeadingDocument: sub_heading_index,
    CommodityDocument: commodity_index,
}


PATTERN = "{}-*"


def rebuild():
    """Create a new index with a unique name, populate it with objects from database and
    create / reassign an alias once the population is done.
    From inside the application only the alias should be referred to.

    """

    es = connections.get_connection()

    for doc, old_index_or_alias in indices.items():
        alias = old_index_or_alias._name
        pattern = PATTERN.format(alias)

        is_alias = es.indices.exists_alias(name=alias)

        new_index_name = pattern.replace("*", dt.datetime.now().strftime("%Y%m%d%H%M%S"))
        new_index = old_index_or_alias.clone(new_index_name)
        new_index.save()

        doc._doc_type.index = new_index_name
        logger.info("Populating index %s", new_index_name)
        doc_inst = doc()
        qs = doc_inst.get_queryset()

        doc_inst.update(qs)
        logger.info("Done!")

        if is_alias:
            logger.info("Swapping aliases to %s -> %s..", new_index_name, alias)
            es.indices.update_aliases(
                body={
                    "actions": [
                        {"remove": {"alias": alias, "index": pattern}},
                        {"add": {"alias": alias, "index": new_index_name}},
                    ]
                }
            )
        else:
            logger.info("Deleting old index..")
            old_index_or_alias.delete()
            logger.info("Adding alias for %s -> %s", new_index_name, alias)
            es.indices.put_alias(index=new_index_name, name=alias)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # initiate the default connection to elasticsearch
        connections.create_connection()

        rebuild()
