"""
Work in progress Haystack search indexes.
"""
from haystack import indexes

from hierarchy.models import Heading

# todo: this seems to supports elasticsearch 6: https://github.com/sabricot/django-elasticsearch-dsl

'''
class CommodityIndex(indexes.SearchIndex, indexes.Indexable):

    commodity_pk = indexes.IntegerField(model_attr='pk')
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/commodity_text.txt')

    def get_model(self):
        return Commodity

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class SubHeadingIndex(indexes.SearchIndex, indexes.Indexable):

    subheading_pk = indexes.IntegerField(model_attr='pk')
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/commodity_text.txt')

    def get_model(self):
        return SubHeading

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
'''


class HeadingIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/heading_text.txt')

    def get_model(self):
        return Heading

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
