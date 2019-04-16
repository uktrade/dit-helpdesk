import json
import re

from django.db import models
from django.urls import reverse

from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson
from hierarchy.models import SubHeading, Heading, Chapter, Section

COMMODITY_CODE_REGEX = '([0-9]{6})([0-9]{2})([0-9]{2})'
import logging

class Commodity(models.Model):

    commodity_code = models.CharField(max_length=10, unique=True)
    goods_nomenclature_sid = models.CharField(max_length=10)
    productline_suffix = models.CharField(max_length=2, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)

    tts_json = models.TextField(blank=True, null=True)
    tts_heading_json = models.TextField(blank=True, null=True)

    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'hierarchy.Heading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )
    parent_subheading = models.ForeignKey(
        'hierarchy.SubHeading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )

    last_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    @property
    def hierarchy_key(self):
        return 'commodity-%s' % self.pk

    def __str__(self):
        return 'Commodity %s' % self.commodity_code

    def get_absolute_url(self, country_code=None):
        kwargs = {'commodity_code': self.commodity_code}
        if country_code is not None:
            kwargs['country_code'] = country_code.lower()
        return reverse('commodity-detail', kwargs=kwargs)

    @property
    def commodity_code_split(self):
        code_match_obj = re.search(COMMODITY_CODE_REGEX, self.commodity_code)
        return [code_match_obj.group(i) for i in range(1, 4)]

    @property
    def tts_obj(self):
        return CommodityJson(json.loads(self.tts_json))

    @property
    def tts_heading_obj(self):
        return CommodityHeadingJson(json.loads(self.tts_heading_json))

    @property
    def tts_title(self):
        return self.description

    @property
    def tts_heading_description(self):
        return self.description

    def get_heading(self):
        """Got up the hierarchy of sub-headings and return the Heading"""
        obj = self.heading or self.parent_subheading
        while type(obj) is not Heading:
            obj = obj.get_parent()
        return obj

    def get_path(self, parent = None, tree = [], level = 0):
        if not parent:
            tree = []
            parent = self

        if hasattr(parent, 'parent_subheading') and parent.parent_subheading is not None:
            self.get_path(parent.parent_subheading, tree, level)
            tree.append(parent.parent_subheading)
        if hasattr(parent, 'heading') and parent.heading is not None:
            self.get_path(parent.heading, tree, level)
            tree.append(parent.heading)
        elif hasattr(parent, 'chapter') and parent.chapter is not None:
            self.get_path(parent.chapter, tree, level)
            tree.append(parent.chapter)
        elif hasattr(parent, 'section') and parent.section is not None:
            tree.append(parent.section)
        elif self.parent_subheading is not parent:
            self.append_path_children(self.parent_subheading, tree)

        return tree

    def append_path_children(self, parent, tree):
        children = parent.get_hierarchy_children()
        for child in children:
            # if type(child) is Commodity:
            tree.append(child)