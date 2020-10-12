"""
Django models for commodities app
"""
import json
import logging
import re

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse

from countries.models import Country
from hierarchy.helpers import IMPORT_MEASURE_GROUPS
from hierarchy.models import (
    Heading, RulesOfOriginMixin, SubHeading, Chapter, NomenclatureTree,
    RegionHierarchyManager, TreeSelectorMixin, RulesOfOriginMixin,
)
from trade_tariff_service.tts_api import CommodityJson

logger = logging.getLogger(__name__)


class Commodity(models.Model, TreeSelectorMixin, RulesOfOriginMixin):
    """
    Commodity model
    """
    objects = RegionHierarchyManager()
    all_objects = models.Manager()

    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    commodity_code = models.CharField(max_length=10)
    goods_nomenclature_sid = models.CharField(max_length=10)
    productline_suffix = models.CharField(max_length=2)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10)
    parent_goods_nomenclature_sid = models.CharField(max_length=10)
    parent_productline_suffix = models.CharField(max_length=2)
    description = models.TextField()
    number_indents = models.SmallIntegerField()
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    tts_json = models.TextField(blank=True, null=True)

    tts_is_leaf = models.BooleanField()

    heading = models.ForeignKey(
        "hierarchy.Heading",
        blank=True,
        null=True,
        related_name="children_concrete",
        on_delete=models.CASCADE,
    )
    parent_subheading = models.ForeignKey(
        "hierarchy.SubHeading",
        blank=True,
        null=True,
        related_name="children_concrete",
        on_delete=models.CASCADE,
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("commodity_code", "goods_nomenclature_sid", "nomenclature_tree")
        verbose_name_plural = "commodities"

    @property
    def leaf(self):
        return True

    @property
    def hierarchy_key(self):
        """
        Hierarchy key used in the template to identify the node
        :return: string
        """
        return "commodity-%s" % self.pk

    def __str__(self):
        return "Commodity %s" % self.commodity_code

    def get_absolute_url(self, country_code=None):
        """
        does a url reverse lookup to get the url of the instance using the country code parameter to filter the results
        :param country_code: string
        :return: url
        """
        kwargs = {
            "commodity_code": self.commodity_code,
            "nomenclature_sid": self.goods_nomenclature_sid,
        }
        if country_code is not None:
            kwargs["country_code"] = country_code.lower()
            kwargs["nomenclature_sid"] = self.goods_nomenclature_sid
        return reverse("commodity-detail", kwargs=kwargs)

    @property
    def commodity_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 4 digits, 2 digits, 2 digits and 2 digits
        :return: list
        """
        code_match_obj = re.search(settings.COMMODITY_CODE_REGEX, self.commodity_code)
        return [code_match_obj.group(i) for i in range(1, 5)]

    @property
    def tts_obj(self):
        """
        gets the json object from the tts_json field and converts it to a python CommodityJson class instance
        used to extract data from the json data structure to display in the template
        :return: CommodityJson object
        """
        return CommodityJson(json.loads(self.tts_json))

    def get_chapter(self):
        """
        returns the chapter for this commodity via the heading
        :return: Chapter object
        """
        return self.get_heading().chapter

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

        if (
            hasattr(parent, "parent_subheading")
            and parent.parent_subheading is not None
        ):
            self.get_path(parent.parent_subheading, tree, level + 1)
            tree.insert(1, [parent.parent_subheading])
        if hasattr(parent, "heading") and parent.heading is not None:
            self.get_path(parent.heading, tree, level + 1)
            tree[level].append(parent.heading)
        elif hasattr(parent, "chapter") and parent.chapter is not None:
            self.get_path(parent.chapter, tree, level + 1)
            tree[level].append(parent.chapter)
        elif hasattr(parent, "section") and parent.section is not None:
            tree[level].append(parent.section)

        if isinstance(parent, Commodity):
            tree.insert(0, [self])

        return tree

    @property
    def ancestor_data(self):
        ancestors = self.get_ancestor_data()
        ancestors.reverse()
        return json.dumps(ancestors)

    def get_ancestor_data(self, parent=None, tree=None, level=0):
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

        if (
            hasattr(parent, "parent_subheading")
            and parent.parent_subheading is not None
        ):
            self.get_ancestor_data(parent.parent_subheading, tree, level + 1)
            tree.insert(
                1,
                [
                    {
                        "id": parent.parent_subheading.id,
                        "description": parent.parent_subheading.description,
                        "commodity_code": parent.parent_subheading.commodity_code,
                        "type": "sub_heading",
                    }
                ],
            )
        if hasattr(parent, "heading") and parent.heading is not None:
            self.get_ancestor_data(parent.heading, tree, level + 1)
            tree[level].append(
                {
                    "id": parent.heading.id,
                    "description": parent.heading.description,
                    "commodity_code": parent.heading.commodity_code,
                    "type": "heading",
                }
            )
        elif hasattr(parent, "chapter") and parent.chapter is not None:
            self.get_ancestor_data(parent.chapter, tree, level + 1)
            tree[level].append(
                {
                    "id": parent.chapter.id,
                    "description": parent.chapter.description,
                    "commodity_code": parent.chapter.commodity_code,
                    "type": "chapter",
                }
            )
        elif hasattr(parent, "section") and parent.section is not None:
            tree[level].append(
                {
                    "id": parent.section.id,
                    "description": parent.section.title,
                    "commodity_code": parent.section.roman_numeral,
                    "type": "section",
                }
            )
        elif self.parent_subheading is not parent:
            self._append_descendant_data(self.parent_subheading, tree, level)

        return tree

    @staticmethod
    def _append_descendant_data(parent, tree, level):
        """
        Appends a tree of descendants to the passed tree from passed parent
        :param parent: parent model instance
        :param tree: list of descendants
        :param level: int
        """
        try:
            children = parent.get_hierarchy_children()
            for child in children:
                if child.commodity_code not in ["9900000000", "9950000000"]:
                    tree[level].append(
                        {
                            "id": child.id,
                            "description": child.description,
                            "commodity_code": child.commodity_code,
                            "type": child._meta.model_name,
                        }
                    )
        except Exception as err:
            logger.debug("_append descendant data".format(err.args))

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
            tree[level].append(child)

    @staticmethod
    def _amend_measure_conditions(resp_content):
        """
        Modifies the structure of the json to find and display related import measures in the template
        :param resp_content: json data from api call
        :return: json string
        """

        obj = json.loads(resp_content)
        if "import_measures" in obj:
            for idx, measure in enumerate(obj["import_measures"]):
                measure["measure_id"] = idx
                for i, condition in enumerate(measure["measure_conditions"]):
                    if isinstance(condition, dict):
                        condition["measure_id"] = idx
                        condition["condition_id"] = i

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

    def get_hierarchy_children(self):
        return []

    def get_parent(self):
        return self.heading or self.parent_subheading
