from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, TextField, fields

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading, Section, Chapter
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@INDEX.doc_type
class CommodityDocument(DocType):
    """
    Commodity elasticsearch document
    """

    # heading = fields.ObjectField(properties={
    #     'heading_code': fields.TextField(),
    #     'description': fields.TextField(),
    # })
    #
    # parent_subheading = fields.ObjectField(properties={
    #     'commodity_code': fields.TextField(),
    #     'description': fields.TextField(),
    # })

    id = fields.IntegerField(attr='id')

    commodity_code = fields.KeywordField(
        # analyzer=html_strip,
        # fields={
        #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    description = fields.TextField(
        analyzer=html_strip,
        # fields={
        #     'description.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    keywords = fields.TextField(
        analyzer=html_strip,
        # fields={
        #     'keywords.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    hierarchy_context = fields.TextField(attr='ancestor_data')

    node_id = fields.TextField(attr='hierarchy_key')

    ranking = fields.IntegerField()

    class Meta:
        model = Commodity

    # def get_queryset(self):
    #     """Not mandatory but to improve performance we can select related in one sql request"""
    #     return super(CommodityDocument, self).get_queryset().select_related(
    #         'heading', 'parent_subheading'
    #     )
    #
    # def get_instances_from_related(self, related_instance):
    #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
    #     The related_models option should be used with caution because it can lead in the index
    #     to the updating of a lot of items.
    #     """
    #     if isinstance(related_instance, Heading):
    #         return related_instance.children_concrete
    #     elif isinstance(related_instance, SubHeading):
    #         return related_instance.children_concrete


