from django.conf import settings
from django_elasticsearch_dsl import Document, fields, Index

from hierarchy.models import Section
from search.documents.util import html_strip

alias = settings.ELASTICSEARCH_INDEX_NAMES[__name__]
INDEX = Index(alias)

# See Elasticsearch Indices API reference for available settings
INDEX.settings(number_of_shards=1, number_of_replicas=0)


@INDEX.doc_type
class SectionDocument(Document):
    """
    Chapter elasticsearch document
    """

    class Django:
        model = Section

    id = fields.IntegerField(attr="section_id")

    nomenclature_tree_id = fields.IntegerField(attr="nomenclature_tree_id")

    commodity_code = fields.KeywordField(attr="section_id")

    description = fields.TextField(attr="title", analyzer=html_strip)

    keywords = fields.TextField(analyzer=html_strip)

    hierarchy_context = fields.TextField(attr="ancestor_data")

    node_id = fields.TextField(attr="hierarchy_key")

    ranking = fields.IntegerField()

    leaf = fields.BooleanField(attr="leaf")
