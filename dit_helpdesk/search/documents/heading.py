from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading, Chapter
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@INDEX.doc_type
class HeadingDocument(DocType):
    """
    Heading elasticsearch document
    """
    # chapter = fields.ObjectField(properties={
    #     'chapter_code': fields.TextField(),
    #     'description': fields.TextField(),
    # })
    #
    # child_subheadings = fields.ObjectField(properties={
    #     'commodity_code': fields.TextField(),
    #     'description': fields.TextField(),
    # })
    #
    # children_concrete = fields.NestedField(properties={
    #     'description': fields.TextField(),
    #     'commodity_code': fields.TextField(),
    #     'pk': fields.IntegerField(),
    # })
    id = fields.IntegerField(attr='id')

    commodity_code = fields.KeywordField(
        attr="heading_code",
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

    ranking = fields.IntegerField()

    class Meta:
        model = Heading

        # related_models = [SubHeading, Commodity]

    # def get_queryset(self):
    #     """Not mandatory but to improve performance we can select related in one sql request"""
    #     return super(HeadingDocument, self).get_queryset().select_related(
    #         'chapter'
    #     )
    #
    # def get_instances_from_related(self, related_instance):
    #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
    #     The related_models option should be used with caution because it can lead in the index
    #     to the updating of a lot of items.
    #     """
    #     if isinstance(related_instance, Chapter):
    #         return related_instance.headings.all()
    #     elif isinstance(related_instance, SubHeading):
    #         return related_instance.heading
    #     elif isinstance(related_instance, Commodity):
    #         return related_instance.heading
