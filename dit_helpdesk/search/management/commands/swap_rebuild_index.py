import datetime as dt
import logging
import contextlib

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from elasticsearch_dsl import connections

from search.documents.section import SectionDocument, INDEX as section_index
from search.documents.chapter import ChapterDocument, INDEX as chapter_index
from search.documents.heading import HeadingDocument, INDEX as heading_index
from search.documents.subheading import SubHeadingDocument, INDEX as sub_heading_index
from search.documents.commodity import CommodityDocument, INDEX as commodity_index

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import delete_all_inactive_trees

from core.helpers import Timer


logger = logging.getLogger(__name__)


indices = {
    SectionDocument: section_index,
    ChapterDocument: chapter_index,
    HeadingDocument: heading_index,
    SubHeadingDocument: sub_heading_index,
    CommodityDocument: commodity_index,
}

ALIAS_PATTERN = settings.ELASTICSEARCH_ALIAS_PATTERN

# this pattern is used to discern index names {alias}-{datetime} - e.g. section-20200615123123
# by using e.g. `section-*` in ElasticSearch calls we can reassign the alias without worrying what
# was the actual datetime in the name of the index
INDEX_PATTERN = "{}-*"


timer = Timer()


@contextlib.contextmanager
def swap_index_name(document, new_name):
    old_name = document._index._name
    document._index._name = new_name

    yield

    document._index._name = old_name


def rebuild(tree):
    """Create a new index with a unique name, populate it with objects from database and
    create / reassign an alias once the population is done.
    From inside the application only the alias should be referred to.

    """
    es = connections.get_connection()

    indices_names_to_remove_conditionally = []
    indices_to_remove_before_creating_alias = []
    update_aliases_actions = []
    new_aliases = []

    for doc, old_index_or_alias in indices.items():
        old_alias = old_index_or_alias._name
        new_alias = ALIAS_PATTERN.format(model_name=old_alias, region=tree.region)

        old_pattern = INDEX_PATTERN.format(old_alias)     # e.g. `section-*`
        new_pattern = INDEX_PATTERN.format(new_alias)     # e.g. `section-uk-*`

        # get old concrete index(es) the alias was pointing to previously so that we can delete
        # it if we want. We can also just keep them even if the alias does not point to them
        # anymore
        old_indices_by_old_alias = list(es.indices.get(index=old_pattern).keys())
        old_indices_by_new_alias = list(es.indices.get(index=new_pattern).keys())

        indices_names_to_remove_conditionally.extend(old_indices_by_old_alias)
        indices_names_to_remove_conditionally.extend(old_indices_by_new_alias)

        # build a concrete index name from the pattern
        new_index_name = new_pattern.replace("*", dt.datetime.now().strftime("%Y%m%d%H%M%S"))
        new_index = old_index_or_alias.clone(new_index_name)
        logger.info("Creating new index %s..", new_index_name)
        new_index.save()

        logger.info("Populating index %s", new_index_name)

        # `doc` is e.g. `SectionDocument`
        doc_inst = doc()

        with swap_index_name(doc_inst, new_index_name):
            doc_inst._index._name = new_index_name
            model = doc.Django.model
            qs = model.all_objects.filter(nomenclature_tree=tree)

            doc_inst.update(qs)
        logger.info("Done!")

        if tree.region == settings.PRIMARY_REGION:
            # to maintain backwards compatibility, at least at first, keep the old style alias for
            # the primary region index (i.e. UK would have both `section` and `section-uk` aliases)
            update_aliases_actions.extend(
                [
                    {"remove": {"alias": old_alias, "index": "*"}},
                    {"add": {"alias": old_alias, "index": new_index_name}},
                ]
            )

        update_aliases_actions.extend(
            [
                {"remove": {"alias": new_alias, "index": new_pattern}},
                {"add": {"alias": new_alias, "index": new_index_name}},
            ]
        )

    # the only time frame during which results could be slightly inconsistent (i.e. new results
    # in search, old in detail) - is between this point and the point when the transaction
    # exits (which is when the DB is updated with the transaction state and the detail view is
    # updated) - probably this time frame is in the order of milliseconds
    timer.start()

    if update_aliases_actions:
        logger.info("Updating aliases: %s", update_aliases_actions)
        es.indices.update_aliases(
            body={
                "actions": update_aliases_actions,
            }
        )

    # if there was a concrete index using the same name as the alias we plan to use, we have to
    # delete it before we use this alias
    for index in indices_to_remove_before_creating_alias:
        logger.info("Removing index %s", index)
        index.delete()

    for index, alias in new_aliases:
        logger.info("Adding alias for %s -> %s", index, alias)
        es.indices.put_alias(index=index, name=alias)

    return indices_names_to_remove_conditionally


def swap_rebuild_single_index(latest_tree, keep_old_trees=False, keep_old_indices=False):

    with transaction.atomic():
        # get latest tree - not yet active because we want to activate it only immediately after
        # finishing reindexing (and swapping index aliases)
        new_tree = latest_tree

        # get active (but not latest) tree
        prev_tree = NomenclatureTree.get_active_tree(settings.PRIMARY_REGION)

        if prev_tree:
            prev_tree.end_date = timezone.now()
            prev_tree.save()

        # activate the latest tree so that ES indexes objects from that tree (but it's not
        # yet visible in the app since the transaction didn't finish)
        new_tree.end_date = None
        new_tree.save()
        indices_names_to_remove_conditionally = rebuild(new_tree)

    timer.stop()

    logger.info("Time spent in inconsistent state: %sms", timer.elapsed() * 1000)

    # once transaction finishes both ES index and DB objects should point to the new objects

    if not keep_old_trees:
        with transaction.atomic():
            delete_all_inactive_trees(latest_tree.region)

    if not keep_old_indices:
        es = connections.get_connection()

        for index in indices_names_to_remove_conditionally:
            logger.info("Removing index %s", index)
            es.indices.delete(index=index)


class Command(BaseCommand):

    help = "Populate ElasticSearch index with data from the most recently created NomenclatureTree"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-old-trees", action="store_true", default=False,
            help="Keep previous NomenclatureTrees, even if they are not marked as active")
        parser.add_argument(
            "--keep-old-indices", action="store_true", default=False,
            help="Keep previous ElasticSearch indices, even if no alias points to them anymore")

    def handle(self, *args, **options):
        # initiate the default connection to elasticsearch
        connections.create_connection(hosts=settings.ES_URL)

        for latest_tree in NomenclatureTree.get_all_latest_trees():
            swap_rebuild_single_index(
                latest_tree,
                keep_old_trees=options['keep_old_trees'],
                keep_old_indices=options['keep_old_indices']
            )
