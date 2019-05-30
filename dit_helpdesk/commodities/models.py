"""
Django models for commodities app
"""
import json
import re

import requests
from django.conf import settings
from django.db import models
from django.urls import reverse

from countries.models import Country
from hierarchy.models import SubHeading, Heading, Chapter, Section
from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson


class Commodity(models.Model):
    """
    Commodity model
    """
    commodity_code = models.CharField(max_length=10, unique=True)
    goods_nomenclature_sid = models.CharField(max_length=10)
    productline_suffix = models.CharField(max_length=2, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField()

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
        verbose_name_plural = "commodities"

    @property
    def hierarchy_key(self):
        """
        Hierarchy key used in the template to identify the node
        :return: string
        """
        return 'commodity-%s' % self.pk

    def __str__(self):
        return 'Commodity %s' % self.commodity_code

    def get_absolute_url(self, country_code=None):
        """
        does a url reverse lookup to get the url of the instance using the country code parameter to filter the results
        :param country_code: string
        :return: url
        """
        kwargs = {'commodity_code': self.commodity_code}
        if country_code is not None:
            kwargs['country_code'] = country_code.lower()
        return reverse('commodity-detail', kwargs=kwargs)

    @property
    def commodity_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 6 digits, 2 digits and 2 digits
        :return: list
        """
        code_match_obj = re.search(settings.COMMODITY_CODE_REGEX, self.commodity_code)
        return [code_match_obj.group(i) for i in range(1, 4)]

    @property
    def tts_obj(self):
        """
        gets the json object from the tts_json field and converts it to a python CommodityJson class instance
        used to extract data from the json data structure to display in the template
        :return: CommodityJson object
        """
        return CommodityJson(json.loads(self.tts_json))

    @property
    def tts_heading_obj(self):
        """
        gets the json object from the tts_heading_json field and converts it to a python CommodityHeadingJson class
        instance
        used to extract data from the json data structure to display in the template
        :return: CommodityHeadingJson object
        """
        return CommodityHeadingJson(json.loads(self.tts_heading_json))

    @property
    def tts_title(self):
        """
        Extracts the Commodity title from the json data to display in the template
        :return: string
        """
        return self.description

    @property
    def tts_heading_description(self):
        """
        Extracts the Commodity Heading title from the json data to display in the template
        :return: string
        """
        return self.description

    def get_heading(self):
        """
        returns the commodity's Heading instance
        if the commodity's ancestors are subheadings the hierarchy is recursively traversed until a
        Heading item is reached
        :return: model instance
        """
        obj = self.heading or self.parent_subheading
        while type(obj) is not Heading:
            obj = obj.get_parent()
        return obj

    def get_regulations(self):
        """
        Returns a list of regulations instances either related to the commodity or it's parent subheading
        :return: queryset
        """
        regulations = list(self.regulation_set.all())

        if self.parent_subheading:
            regulations + list(self.parent_subheading.regulation_set.all())

        return regulations

    def get_rules_of_origin(self, country_code):
        """
        Returns a dictionary of related rules of origin instances related to the commodity and filtered by the
        country code parameter.
        the dictionary has two keys one for the list of rules and one for the related footnotes
        :param country_code: string
        :return: dictionary
        """

        country = Country.objects.get(country_code=country_code)
        rules_of_origin = {
            "rules": [],
            "footnotes": []
        }
        for group_member in country.rulesgroupmember_set.all():
            for document in group_member.rules_group.rulesdocument_set.all():
                rules_of_origin['footnotes'] = document.footnotes.all().order_by('id')
                for rule in document.rule_set.all().order_by('id'):
                    if rule.chapter == self.get_heading().chapter:
                        rules_of_origin['rules'].append(rule)
        return rules_of_origin

    def get_path(self, parent=None, tree=None, level=0):
        """
        Returns the context path of the Commodity showing its level in the hierarchy tree
        and its ancestors
        :param parent: parent model instance
        :param tree: list of ancestor instances
        :param level: int
        :return: list
        """
        if tree is None:
            tree = []
        if not parent:
            tree = []
            parent = self

        if len(tree) < level + 1:
            tree.append([])

        if hasattr(parent, 'parent_subheading') and parent.parent_subheading is not None:
            self.get_path(parent.parent_subheading, tree, level + 1)
            tree.insert(1, [parent.parent_subheading])
        if hasattr(parent, 'heading') and parent.heading is not None:
            self.get_path(parent.heading, tree, level + 1)
            tree[level].append(parent.heading)
        elif hasattr(parent, 'chapter') and parent.chapter is not None:
            self.get_path(parent.chapter, tree, level + 1)
            tree[level].append(parent.chapter)
        elif hasattr(parent, 'section') and parent.section is not None:
            tree[level].append(parent.section)
        elif self.parent_subheading is not parent:
            self._append_path_children(self.parent_subheading, tree, level)

        return tree

    @staticmethod
    def _append_path_children(parent, tree, level):
        """
        Appends a tree of descendants to the passed tree from passed parent
        :param parent: parent model instance
        :param tree: list of descendants
        :param level: int
        """
        children = parent.get_hierarchy_children()
        for child in children:
            # if type(child) is Commodity:
            tree[level].append(child)

    @staticmethod
    def _amend_measure_conditions(resp_content):
        """
        Modifies the structure of the json to find and display related import measures in the template
        :param resp_content: json data from api call
        :return: json string
        """
        obj = json.loads(resp_content)
        for idx, measure in enumerate(obj['import_measures']):
            measure['measure_id'] = idx
            for i, condition in enumerate(measure['measure_conditions']):
                if isinstance(condition, dict):
                    condition['measure_id'] = idx
                    condition['condition_id'] = i

        return json.dumps(obj)

    def update_content(self):
        """
        gets the Commodity content from the trade tariff service url as json response and stores it in the
        commodity's tts_json field

        """
        url = settings.COMMODITY_URL % self.commodity_code

        resp = requests.get(url, timeout=10)
        resp_content = None

        if resp.status_code == 200:
            resp_content = resp.content.decode()
        elif resp.status_code == 404:
            url = settings.HEADING_URL % self.commodity_code[:4]
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                resp_content = resp.content.decode()

        resp_content = self._amend_measure_conditions(resp_content)

        self.tts_json = resp_content
        self.save()
