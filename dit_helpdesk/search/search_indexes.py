"""
Work in progress Haystack search indexes.
"""
import datetime
from haystack import indexes

from commodities.models import Commodity
from hierarchy.models import Heading

# todo: this seems to supports elasticsearch 6: https://github.com/sabricot/django-elasticsearch-dsl


class CommodityIndex(indexes.SearchIndex, indexes.Indexable):

    commodity_pk = indexes.IntegerField(model_attr='pk')
    commodity_code = indexes.CharField(model_attr="commodity_code") # template_name='search/indexes/commodity_text.txt'
    description = indexes.CharField(model_attr="description", )  # template_name='search/indexes/commodity_text.txt'
    text = indexes.CharField(document=True, use_template=True)
    last_updated = indexes.DateTimeField(model_attr='last_updated')

    def get_model(self):
        return Commodity

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(last_updated__lte=datetime.datetime.now())

'''
class SubHeadingIndex(indexes.SearchIndex, indexes.Indexable):

    subheading_pk = indexes.IntegerField(model_attr='pk')
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/commodity_text.txt')

    def get_model(self):
        return SubHeading

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
'''


# class HeadingIndex(indexes.SearchIndex, indexes.Indexable):
#
#     text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/heading_text.txt')
#
#     def get_model(self):
#         return Heading
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.all()
