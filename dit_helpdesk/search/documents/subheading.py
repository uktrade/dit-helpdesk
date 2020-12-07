from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from hierarchy.models import SubHeading
from search.documents.util import html_strip

alias = settings.ELASTICSEARCH_INDEX_NAMES[__name__]
alias_pattern = settings.ELASTICSEARCH_ALIAS_PATTERNS[__name__]
INDEX = Index(alias)

# See Elasticsearch Indices API reference for available settings
INDEX.settings(number_of_shards=1, number_of_replicas=0)


@INDEX.doc_type
class SubHeadingDocument(Document):
    """
    SubHeading elasticsearch document
    """

    class Django:
        model = SubHeading

    id = fields.IntegerField(attr="goods_nomenclature_sid")

    nomenclature_tree_id = fields.IntegerField(attr="nomenclature_tree_id")

    commodity_code = fields.KeywordField()

    description = fields.TextField(analyzer=html_strip)

    keywords = fields.TextField(analyzer=html_strip)

    hierarchy_context = fields.TextField(attr="ancestor_data")

    node_id = fields.TextField(attr="hierarchy_key")

    ranking = fields.IntegerField()

    leaf = fields.BooleanField(attr="leaf")
