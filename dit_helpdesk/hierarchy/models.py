import json
import logging
import re

import requests
from django.conf import settings
from django.db import models
from django.urls import reverse

from countries.models import Country
from trade_tariff_service.tts_api import HeadingJson, SubHeadingJson, ChapterJson

logger = logging.getLogger(__name__)

CHAPTER_CODE_REGEX = "([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})"


class NomenclatureTree(models.Model):
    """
    Model to identify which tree does a nomenclature object belong to, differentiated
    by region (e.g. `EU`, `UK`) and date range.

    """
    region = models.CharField(max_length=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True)


class Section(models.Model):
    """
    Model representing the top level section of the hierarchy
    """

    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)
    section_id = models.IntegerField(unique=True)
    tts_json = models.TextField(blank=True)
    roman_numeral = models.CharField(max_length=5)
    title = models.TextField()
    position = models.IntegerField()
    keywords = models.TextField(null=True)
    ranking = models.SmallIntegerField(null=True)

    def __str__(self):
        return "Section {0}".format(self.roman_numeral)

    @property
    def leaf(self):
        return False

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return "section-%s" % self.section_id

    @property
    def chapter_range_str(self):
        """
        Property method returning a string representing the range of chapters in this section
        :return:  string
        """
        chapter_codes = [
            int(chapter.chapter_code[:2]) for chapter in self.chapter_set.all()
        ]
        if len(chapter_codes) == 0:
            return "None"
        if len(chapter_codes) == 1:
            return str(chapter_codes[0])
        min_code, max_code = min(chapter_codes), max(chapter_codes)
        return "%s to %s" % (min_code, max_code)

    def get_hierarchy_children(self):
        """
        Query returning a list of child chapters ordered by code
        :return:
        """
        return self.chapter_set.all().order_by("chapter_code")

    def get_hierarchy_children_count(self):
        """
        Query returning a count of children
        :return: int
        """
        return self.get_hierarchy_children().count()

    def get_chapters_url(self):
        """
        Returns a section url to a view listing the child chapters
        :return:
        """
        return reverse(
            "hierarchy-section-chapters", kwargs={"section_id": str(self.section_id)}
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {"node_id": "section-%s" % self.section_id}

        if country_code is not None:
            kwargs["country_code"] = country_code.lower()

        return reverse("search:search-hierarchy", kwargs=kwargs)

    @property
    def section_notes(self):
        url = "https://www.trade-tariff.service.gov.uk/api/v2/sections/{0}/section_note".format(
            self.section_id
        )
        resp = requests.get(url, timeout=10)
        section_notes = []

        if resp.status_code == 200:
            resp_content = resp.json()

            section_note_items = resp_content["content"].split("\r\n")

            for item in section_note_items:
                match = re.search(r"^\* (\d)\\. (.*)", item)
                if match:
                    section_notes.append(
                        '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-1"><span>{0}.</span><span>{1}</span></div>'.format(
                            match.group(1), match.group(2)
                        )
                    )

                match = re.search(r"^  \* \((\w)\) (.*)", item)
                if match:
                    section_notes.append(
                        '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-2"><span>({0})</span><span>{1}</span></div>'.format(
                            match.group(1), match.group(2)
                        )
                    )

                match = re.search(r"^    ([\s*\\-]*)(.*)", item)
                if match:
                    section_notes.append(
                        '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-3"><span>{0}</span><span>{1}</span></div>'.format(
                            "-", match.group(2)
                        )
                    )

                match = re.search(r"^\* ([^\d.]+)", item)
                if match:
                    section_notes.append(
                        '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__text"><span>{0}</span><span></span></div>'.format(
                            match.group(1)
                        )
                    )

                match = re.search(r"^##(.+)##", item)
                if match:
                    section_notes.append(
                        '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__heading"><span>{0}</span><span></span></div>'.format(
                            match.group(1)
                        )
                    )

        return section_notes

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

        return tree

    def get_parent(self):
        return None


class Chapter(models.Model):
    """
    Model representing the second level chapters of the hierarchy
    """

    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    goods_nomenclature_sid = models.CharField(max_length=10)
    productline_suffix = models.CharField(max_length=2)
    leaf = models.BooleanField()
    parent_goods_nomenclature_item_id = models.CharField(max_length=10)
    parent_goods_nomenclature_sid = models.CharField(max_length=10)
    parent_productline_suffix = models.CharField(max_length=2)
    description = models.TextField()
    number_indents = models.SmallIntegerField()
    keywords = models.TextField(null=True, blank=True)
    ranking = models.SmallIntegerField(null=True, blank=True)
    chapter_code = models.CharField(max_length=30)
    tts_json = models.TextField(blank=True, null=True)

    section = models.ForeignKey(
        "Section", blank=True, null=True, on_delete=models.CASCADE
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Chapter {0}".format(self.chapter_code)

    @staticmethod
    def _amend_measure_conditions(resp_content):
        """
        Modifies the structure of the json to find and display related import measures in the template
        :param resp_content: json data from api call
        :return: json string
        """

        obj = json.loads(resp_content)
        if "import_measures" in obj.keys():
            for idx, measure in enumerate(obj["import_measures"]):
                measure["measure_id"] = idx
                for i, condition in enumerate(measure["measure_conditions"]):
                    if isinstance(condition, dict):
                        condition["measure_id"] = idx
                        condition["condition_id"] = i

        return json.dumps(obj)

    @property
    def commodity_code(self):
        return self.chapter_code

    @property
    def title(self):
        """
        Property method returning the Chapter title from the object field
        :return: string
        """
        return self.description

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return "chapter-%s" % self.goods_nomenclature_sid

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.chapter_code

    def get_hierarchy_children(self):
        """
        Query returning a list of child Headings ordered by code
        :return:
        """
        return self.headings.all().order_by("heading_code")

    def get_hierarchy_children_count(self):
        """
        Query returning a count of children
        :return: int
        """
        return self.get_hierarchy_children().count()

    def get_headings_url(self):
        """
        Returns a chapter url to a view listing the child headings
        :return:
        """
        return reverse(
            "hierarchy-section-chapter-headings",
            kwargs={"chapter_code_2": self.chapter_code[:2]},
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {"node_id": "chapter-%s" % self.goods_nomenclature_sid}

        if country_code is not None:
            kwargs["country_code"] = country_code.lower()

        return reverse("search:search-hierarchy", kwargs=kwargs)

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

        if hasattr(parent, "section") and parent.section is not None:
            tree[level].append(
                {
                    "id": parent.section.id,
                    "description": parent.section.title,
                    "commodity_code": parent.section.roman_numeral,
                    "type": "section",
                }
            )

        return tree

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
        elif self.parent_subheading is not parent:
            self._append_path_children(self.parent_subheading, tree, level)

        return tree

    def get_path_children(self):
        return self._append_path_children(self, tree=[[]], level=0)

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

    @property
    def chapter_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 6 digits, 2 digits and 2 digits
        :return: list
        """

        code_match_obj = re.search(CHAPTER_CODE_REGEX, self.chapter_code)
        return [
            code_match_obj.group(i)
            for i in range(1, 5)
            if code_match_obj.group(i) != "00"
        ]

        # gets the Commodity content from the trade tariff service url as json response and stores
        # it in the commodity's tts_json field
        # TODO: unreachable code below, audit if OK to delete

        url = settings.HEADING_URL % self.heading_code[:4]

        resp = requests.get(url, timeout=10)
        resp_content = None

        if resp.status_code == 200:
            resp_content = resp.content.decode()

        resp_content = self._amend_measure_conditions(resp_content)
        self.tts_json = resp_content
        self.save()

    def update_content(self):
        url = settings.CHAPTER_URL.format(self.chapter_code[:2])

        resp = requests.get(url, timeout=10)
        resp_content = None
        if resp.status_code == 200:
            resp_content = resp.content.decode()

        self.tts_json = resp_content
        self.save()

    @property
    def tts_obj(self):
        """
        gets the json object from the tts_json field and converts it to a python CommodityJson class instance
        used to extract data from the json data structure to display in the template
        :return: CommodityJson object
        """
        return ChapterJson(json.loads(self.tts_json))

    @property
    def chapter_notes(self):

        if not self.tts_json:
            return []
        chapter_note = self.tts_obj.chapter_note

        chapter_note_items = chapter_note.split("\r\n")

        chapter_notes = []
        for item in chapter_note_items:
            match = re.search(r"^\* (\d)\\. (.*)", item)
            if match:
                chapter_notes.append(
                    '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-1"><span>{0}.</span><span>{1}</span></div>'.format(
                        match.group(1), match.group(2)
                    )
                )

            match = re.search(r"^  \* \((\w)\) (.*)", item)
            if match:
                chapter_notes.append(
                    '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-2"><span>({0})</span><span>{1}</span></div>'.format(
                        match.group(1), match.group(2)
                    )
                )

            match = re.search(r"^    ([\s*\\-]*)(.*)", item)
            if match:
                chapter_notes.append(
                    '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__level-3"><span>{0}</span><span>{1}</span></div>'.format(
                        "-", match.group(2)
                    )
                )

            match = re.search(r"^\* ([^\d.]+)", item)
            if match:
                chapter_notes.append(
                    '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__text"><span>{0}</span><span></span></div>'.format(
                        match.group(1)
                    )
                )

            match = re.search(r"^##(.+)##", item)
            if match:
                chapter_notes.append(
                    '<div class="helpdesk-chapter-note-item helpdesk-chapter-note-item__heading"><span>{0}</span><span></span></div>'.format(
                        match.group(1)
                    )
                )

        return chapter_notes

    def get_parent(self):
        return self.section


class Heading(models.Model):
    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    goods_nomenclature_sid = models.CharField(max_length=10)
    productline_suffix = models.CharField(max_length=2)
    leaf = models.BooleanField()
    parent_goods_nomenclature_item_id = models.CharField(max_length=10)
    parent_goods_nomenclature_sid = models.CharField(max_length=10)
    parent_productline_suffix = models.CharField(max_length=2)
    description = models.TextField()
    number_indents = models.SmallIntegerField()
    keywords = models.TextField(null=True, blank=True)
    ranking = models.SmallIntegerField(null=True, blank=True)
    heading_code = models.CharField(max_length=10)
    heading_code_4 = models.CharField(max_length=4, null=True, blank=True)
    tts_json = models.TextField(blank=True, null=True)
    chapter = models.ForeignKey(
        "hierarchy.Chapter",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="headings",
    )
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def commodity_code(self):
        return self.heading_code

    @property
    def tts_obj(self):
        """
        gets the json object from the tts_json field and converts it to a python CommodityJson class instance
        used to extract data from the json data structure to display in the template
        :return: CommodityJson object
        """
        return HeadingJson(json.loads(self.tts_json))

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
            tree[level].append(child)

    @property
    def heading_notes(self):

        if not self.tts_json:
            return {}
        return self.tts_obj.footnotes

    def get_rules_of_origin(self, country_code):
        """
        Returns a dictionary of related rules of origin instances related to the commodity and filtered by the
        country code parameter.
        the dictionary has two keys one for the list of rules and one for the related footnotes
        :param country_code: string
        :return: dictionary
        """

        country = Country.objects.get(country_code=country_code)
        groups = {}
        rules_of_origin = {"rules": [], "footnotes": []}
        for group_member in country.rulesgroupmember_set.all():
            for document in group_member.rules_group.rulesdocument_set.all():
                rules_of_origin["footnotes"] = document.footnotes.all().order_by("id")
                for rule in document.rule_set.all().order_by("id"):
                    if rule.chapter == self.chapter:
                        rules_of_origin["rules"].append(rule)
            group_name = group_member.rules_group.description
            groups[group_name] = rules_of_origin

        return groups

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return "heading-%s" % self.goods_nomenclature_sid

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.heading_code

    def __str__(self):
        return "Heading {0}".format(self.heading_code)

    def get_absolute_url(self, country_code=None):
        """
        Method returning the rul of the current instance
        :return:
        """
        kwargs = {"heading_code": self.heading_code}
        if country_code is not None:
            kwargs["country_code"] = country_code.lower()
            kwargs["nomenclature_sid"] = self.goods_nomenclature_sid
        return reverse("heading-detail", kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [
            obj for obj in self.child_subheadings.all().order_by("commodity_code")
        ]
        commodities = [
            obj for obj in self.children_concrete.all().order_by("commodity_code")
        ]
        return sub_headings + commodities

    def get_hierarchy_children_count(self):
        """
        Query returning a count of children
        :return: int
        """
        return self.child_subheadings.count() + self.children_concrete.count()

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {"node_id": "heading-%s" % self.goods_nomenclature_sid}

        if country_code is not None:
            kwargs["country_code"] = country_code.lower()

        return reverse("search:search-hierarchy", kwargs=kwargs)

    def update_content(self):
        """
        gets the Commodity content from the trade tariff service url as json response and stores it in the
        commodity's tts_json field

        """
        url = settings.HEADING_URL % self.heading_code[:4]

        resp = requests.get(url, timeout=10)
        resp_content = None

        if resp.status_code == 200:
            resp_content = resp.content.decode()

        resp_content = self._amend_measure_conditions(resp_content)
        self.tts_json = resp_content
        self.save()

    @staticmethod
    def _amend_measure_conditions(resp_content):
        """
        Modifies the structure of the json to find and display related import measures in the template
        :param resp_content: json data from api call
        :return: json string
        """
        obj = json.loads(resp_content)
        if "import_measures" in obj.keys():
            for idx, measure in enumerate(obj["import_measures"]):
                measure["measure_id"] = idx
                for i, condition in enumerate(measure["measure_conditions"]):
                    if isinstance(condition, dict):
                        condition["measure_id"] = idx
                        condition["condition_id"] = i

        return json.dumps(obj)

    def is_duplicate_heading(self):
        children = self.get_hierarchy_children()
        duplicate_child = [
            child.commodity_code
            for child in children
            if child.commodity_code == self.heading_code and not child.leaf
        ]
        return True if duplicate_child else False

    @property
    def ancestor_data(self):
        ancestors = self.get_ancestor_data()
        ancestors.reverse()
        return json.dumps(ancestors)

    def get_ancestor_data(self, parent=None, tree=None, level=0):
        """
        Returns the context path of the heading showing its level in the hierarchy tree
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

        if hasattr(parent, "chapter") and parent.chapter is not None:
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

        return tree

    @property
    def heading_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 6 digits, 2 digits and 2 digits
        :return: list
        """
        code_match_obj = re.search(settings.COMMODITY_CODE_REGEX, self.heading_code)
        code = [code_match_obj.group(i) for i in range(1, 5)]

        if not self.leaf:
            return code[:1]
        else:
            return code

    def get_parent(self):
        return self.chapter


class SubHeading(models.Model):
    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    productline_suffix = models.CharField(max_length=2)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10)
    parent_goods_nomenclature_sid = models.CharField(max_length=10)
    parent_productline_suffix = models.CharField(max_length=2)
    description = models.TextField()
    number_indents = models.SmallIntegerField()
    keywords = models.TextField(null=True, blank=True)
    ranking = models.SmallIntegerField(null=True, blank=True)
    commodity_code = models.CharField(max_length=10)  # goods_nomenclature_item_id
    goods_nomenclature_sid = models.CharField(max_length=10)
    leaf = models.BooleanField()
    tts_json = models.TextField(blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    @property
    def heading_code_4(self):
        return self.commodity_code[:4]

    heading = models.ForeignKey(
        "hierarchy.Heading",
        blank=True,
        null=True,
        related_name="child_subheadings",
        on_delete=models.CASCADE,
    )

    parent_subheading = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="child_subheadings",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("commodity_code", "description")

    def __str__(self):
        return "Sub Heading {0}".format(self.commodity_code)

    def get_absolute_url(self, country_code=None):
        """
        Method returning the rul of the current instance
        :return:
        """
        kwargs = {"commodity_code": self.commodity_code}
        if country_code is not None:
            kwargs["country_code"] = country_code.lower()
            kwargs["nomenclature_sid"] = self.goods_nomenclature_sid
        return reverse("subheading-detail", kwargs=kwargs)

    def is_duplicate_heading(self):
        children = self.get_hierarchy_children()
        duplicate_child = [
            child.commodity_code
            for child in children
            if child.commodity_code == self.commodity_code and not child.leaf
        ]
        return True if duplicate_child else False

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return "sub_heading-%s" % self.goods_nomenclature_sid

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.commodity_code

    def get_parent(self):
        """
        Method to return the parent Heading or Subheading of the current instance
        :return: Model instance
        """
        return self.heading or self.parent_subheading

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {"node_id": "sub_heading-%s" % self.goods_nomenclature_sid}

        if country_code is not None:
            kwargs["country_code"] = country_code.lower()

        return reverse("search:search-hierarchy", kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [
            obj for obj in self.child_subheadings.all().order_by("commodity_code")
        ]
        commodities = [
            obj for obj in self.children_concrete.all().order_by("commodity_code")
        ]
        return commodities + sub_headings

    def get_hierarchy_children_count(self):
        """
        Query returning a count of children
        :return: int
        """
        return self.child_subheadings.count() + self.children_concrete.count()

    @property
    def heading_notes(self):

        notes = None
        path = self.get_path()

        for item in path:
            if len(item) > 0:
                if item[0].tts_json is not None:
                    if isinstance(item[0], SubHeading) or isinstance(item[0], Heading):
                        footnotes = item[0].tts_obj.footnotes
                        if footnotes:
                            if notes is not None:
                                if isinstance(notes, dict):
                                    notes.update(footnotes)
                                elif isinstance(notes, list):
                                    notes.extend(footnotes)
                            else:
                                notes = footnotes
        return notes

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

        return tree

    def update_content(self):
        """
        gets the Commodity content from the trade tariff service url as json response and stores it in the
        commodity's tts_json field

        """
        url = settings.HEADING_URL % self.commodity_code[:4]

        resp = requests.get(url, timeout=10)
        resp_content = None

        if resp.status_code == 200:
            resp_content = resp.content.decode()

        resp_content = self._amend_measure_conditions(resp_content)

        self.tts_json = resp_content

        self.save()

    @staticmethod
    def _amend_measure_conditions(resp_content):
        """
        Modifies the structure of the json to find and display related import measures in the template
        :param resp_content: json data from api call
        :return: json string
        """

        obj = json.loads(resp_content)

        if "import_measures" in obj.keys():
            for idx, measure in enumerate(obj["import_measures"]):
                measure["measure_id"] = idx
                for i, condition in enumerate(measure["measure_conditions"]):
                    if isinstance(condition, dict):
                        condition["measure_id"] = idx
                        condition["condition_id"] = i

        return json.dumps(obj)

    @property
    def tts_obj(self):
        """
        gets the json object from the tts_json field and converts it to a python CommodityJson class instance
        used to extract data from the json data structure to display in the template
        :return: CommodityJson object
        """
        return SubHeadingJson(json.loads(self.tts_json))

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
        # elif self.parent_subheading is not parent:
        #     self._append_path_children(self.parent_subheading, tree, level)

        return tree

    def get_rules_of_origin(self, country_code):
        """
        Returns a dictionary of related rules of origin instances related to the commodity and filtered by the
        country code parameter.
        the dictionary has two keys one for the list of rules and one for the related footnotes
        :param country_code: string
        :return: dictionary
        """

        country = Country.objects.get(country_code=country_code)
        groups = {}
        rules_of_origin = {"rules": [], "footnotes": []}
        for group_member in country.rulesgroupmember_set.all():
            for document in group_member.rules_group.rulesdocument_set.all():
                rules_of_origin["footnotes"] = document.footnotes.all().order_by("id")
                for rule in document.rule_set.all().order_by("id"):
                    if rule.chapter == self.get_chapter():
                        rules_of_origin["rules"].append(rule)
            group_name = group_member.rules_group.description
            groups[group_name] = rules_of_origin

        return groups

    @property
    def subheading_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 6 digits, 2 digits and 2 digits
        :return: list
        """
        code_match_obj = re.search(settings.COMMODITY_CODE_REGEX, self.commodity_code)
        code = [code_match_obj.group(i) for i in range(1, 5)]
        if not self.leaf:
            return [x for x in code if x != "00"]
        else:
            return code

    def get_chapter(self, ancestor=None):
        """
        recursive function to return the ancestoral chapter
        :param ancestor: SubHeading or Heading
        :return: chapter
        """
        if not ancestor:
            ancestor = self.get_parent()

        while not isinstance(ancestor, Heading):
            parent = ancestor.get_parent()
            return self.get_chapter(ancestor=parent)
        else:
            return ancestor.chapter

    def get_path_children(self):
        return self._append_path_children(self, tree=[[]], level=0)

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
