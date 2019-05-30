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

    commodity_code = fields.StringField(
        analyzer=html_strip,
        # fields={
        #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    description = fields.StringField(
        analyzer=html_strip,
        # fields={
        #     'description.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    keywords = fields.StringField(
        analyzer=html_strip,
        # fields={
        #     'keywords.raw': fields.StringField(analyzer="Keyword")
        # }
    )

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


# @INDEX.doc_type
# class SubHeadingDocument(DocType):
#     """
#     SubHeading elasticsearch document
#     """
#     # heading = fields.ObjectField(properties={
#     #     'heading_code': fields.TextField(),
#     #     'description': fields.TextField(),
#     # })
#     #
#     # parent_subheading = fields.ObjectField(properties={
#     #     'commodity_code': fields.TextField(),
#     #     'description': fields.TextField(),
#     # })
#     #
#     # children_concrete = fields.NestedField(properties={
#     #     'description': fields.TextField(),
#     #     'commodity_code': fields.TextField(),
#     #     'pk': fields.IntegerField(),
#     # })
#
#     id = fields.IntegerField(attr='id')
#
#     commodity_code = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     description = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'description.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     keywords = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'keywords.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     ranking = fields.IntegerField()
#
#     class Meta:
#         model = SubHeading
#         # related_models = [Heading, Commodity]
#
#     # def get_queryset(self):
#     #     """Not mandatory but to improve performance we can select related in one sql request"""
#     #     return super(SubHeadingDocument, self).get_queryset().select_related(
#     #         'heading'
#     #     )
#     #
#     # def get_instances_from_related(self, related_instance):
#     #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
#     #     The related_models option should be used with caution because it can lead in the index
#     #     to the updating of a lot of items.
#     #     """
#     #     if isinstance(related_instance, Heading):
#     #         return related_instance.child_subheadings.all()
#     #     elif isinstance(related_instance, Commodity):
#     #         return related_instance.parent_subheading
#
# @INDEX.doc_type
# class SectionDocument(DocType):
#     """
#     Chapter elasticsearch document
#     """
#
#     # chapter_set = fields.NestedField(properties={
#     #     'description': fields.TextField(),
#     #     'chapter_code': fields.TextField()
#     # })
#
#     id = fields.IntegerField(attr='id')
#
#     commodity_code = fields.StringField(
#         attr="section_id",
#         analyzer=html_strip,
#         # fields={
#         #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     description = fields.StringField(
#         attr="title",
#         analyzer=html_strip,
#         # fields={
#         #     'title.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     keywords = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'keywords.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     ranking = fields.IntegerField()
#
#     class Meta:
#         model = Section
#
#         # related_models = [Chapter]
#
#     # def get_instances_from_related(self, related_instance):
#     #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
#     #     The related_models option should be used with caution because it can lead in the index
#     #     to the updating of a lot of items.
#     #     """
#     #     if isinstance(related_instance, Chapter):
#     #         return related_instance.chapter_set.all()
#
# @INDEX.doc_type
# class HeadingDocument(DocType):
#     """
#     Heading elasticsearch document
#     """
#     # chapter = fields.ObjectField(properties={
#     #     'chapter_code': fields.TextField(),
#     #     'description': fields.TextField(),
#     # })
#     #
#     # child_subheadings = fields.ObjectField(properties={
#     #     'commodity_code': fields.TextField(),
#     #     'description': fields.TextField(),
#     # })
#     #
#     # children_concrete = fields.NestedField(properties={
#     #     'description': fields.TextField(),
#     #     'commodity_code': fields.TextField(),
#     #     'pk': fields.IntegerField(),
#     # })
#     id = fields.IntegerField(attr='id')
#
#     commodity_code = fields.StringField(
#         attr="heading_code",
#         analyzer=html_strip,
#         # fields={
#         #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     description = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'description.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     keywords = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'keywords.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     ranking = fields.IntegerField()
#
#     class Meta:
#         model = Heading
#
#         # related_models = [SubHeading, Commodity]
#
#     # def get_queryset(self):
#     #     """Not mandatory but to improve performance we can select related in one sql request"""
#     #     return super(HeadingDocument, self).get_queryset().select_related(
#     #         'chapter'
#     #     )
#     #
#     # def get_instances_from_related(self, related_instance):
#     #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
#     #     The related_models option should be used with caution because it can lead in the index
#     #     to the updating of a lot of items.
#     #     """
#     #     if isinstance(related_instance, Chapter):
#     #         return related_instance.headings.all()
#     #     elif isinstance(related_instance, SubHeading):
#     #         return related_instance.heading
#     #     elif isinstance(related_instance, Commodity):
#     #         return related_instance.heading
#
# @INDEX.doc_type
# class ChapterDocument(DocType):
#     """
#     Chapter elasticsearch document
#     """
#     #
#     # section = fields.ObjectField(properties={
#     #     'section_id': fields.TextField(),
#     #     'title': fields.TextField(),
#     # })
#     #
#     # headings = fields.NestedField(properties={
#     #     'description': fields.TextField(),
#     #     'heading_code': fields.TextField()
#     # })
#
#     id = fields.IntegerField(attr='id')
#
#     commodity_code = fields.StringField(
#         attr="chapter_code",
#         analyzer=html_strip,
#         # fields={
#         #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     description = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'description.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     keywords = fields.StringField(
#         analyzer=html_strip,
#         # fields={
#         #     'keywords.raw': fields.StringField(analyzer="Keyword")
#         # }
#     )
#
#     ranking = fields.IntegerField()
#
#     class Meta:
#         model = Chapter
#
#     #     related_models = [Heading, Section]
#     #
#     # def get_queryset(self):
#     #     """Not mandatory but to improve performance we can select related in one sql request"""
#     #     return super(ChapterDocument, self).get_queryset().select_related(
#     #         'section'
#     #     )
#     #
#     # def get_instances_from_related(self, related_instance):
#     #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
#     #     The related_models option should be used with caution because it can lead in the index
#     #     to the updating of a lot of items.
#     #     """
#     #     if isinstance(related_instance, Section):
#     #         return related_instance.chapter_set.all()
#     #     elif isinstance(related_instance, Heading):
#     #         return related_instance.chapter
