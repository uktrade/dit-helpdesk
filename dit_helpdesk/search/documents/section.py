from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields

from hierarchy.models import Section
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(number_of_shards=1, number_of_replicas=0)


@INDEX.doc_type
class SectionDocument(DocType):
    """
    Chapter elasticsearch document
    """

    id = fields.IntegerField(attr="section_id")

    commodity_code = fields.KeywordField(attr="section_id")

    description = fields.TextField(attr="title", analyzer=html_strip)

    keywords = fields.TextField(analyzer=html_strip)

    hierarchy_context = fields.TextField(attr="ancestor_data")

    node_id = fields.TextField(attr="hierarchy_key")

    ranking = fields.IntegerField()

    class Meta:
        model = Section
