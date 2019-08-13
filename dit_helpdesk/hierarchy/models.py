import json

import requests
from django.conf import settings
from django.db import models
from django.urls import reverse

from countries.models import Country
from trade_tariff_service.tts_api import HeadingJson

ROMAN_NUMERALS = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
    7: 'VII',
    8: 'VIII',
    9: 'IX',
    10: 'X',
    11: 'XI',
    12: 'XII',
    13: 'XIII',
    14: 'XIV',
    15: 'XV',
    16: 'XVI',
    17: 'XVII',
    18: 'XVIII',
    19: 'XIX',
    20: 'XX',
    21: 'XXI'
}


class Section(models.Model):
    """
    Model representing the top level section of the hierarchy
    """

    section_id = models.IntegerField(unique=True)
    tts_json = models.TextField(blank=True, null=True)
    roman_numeral = models.CharField(max_length=5, null=True)
    title = models.TextField(blank=True, null=True)
    position = models.IntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    def __str__(self):
        return "Section {0}".format(self.roman_numeral)

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'section-%s' % self.pk

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
            return 'None'
        if len(chapter_codes) == 1:
            return str(chapter_codes[0])
        min_code, max_code = min(chapter_codes), max(chapter_codes)
        return '%s to %s' % (min_code, max_code)

    def get_hierarchy_children(self):
        """
        Query returning a list of child chapters ordered by code
        :return:
        """
        return self.chapter_set.all().order_by('chapter_code')

    def get_chapters_url(self):
        """
        Returns a section url to a view listing the child chapters
        :return:
        """
        return reverse(
            'hierarchy-section-chapters',
            kwargs={'section_id': str(self.section_id)}
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'section-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)

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

        # tree[level].append({"id": self.id,
        #                     "description": self.title,
        #                     "commodity_code": self.roman_numeral,
        #                     "type": "section"})

        return tree

    # @staticmethod
    # def _append_descendant_data(parent, tree, level):
    #     """
    #     Appends a tree of descendants to the passed tree from passed parent
    #     :param parent: parent model instance
    #     :param tree: list of descendants
    #     :param level: int
    #     """
    #     try:
    #         children = parent.get_hierarchy_children()
    #         for child in children:
    #             # if type(child) is Commodity:
    #             if child.commodity_code not in ["9900000000", "9950000000"]:
    #                 tree[level].append({"id": child.id,
    #                                 "description": child.description,
    #                                 "commodity_code": child.commodity_code,
    #                                 "type": child._meta.model_name})
    #     except Exception as err:
    #         print(err.args)


class Chapter(models.Model):
    """
    Model representing the second level chapters of the hierarchy
    """

    # goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    productline_suffix = models.CharField(max_length=2, null=True)
    leaf = models.BooleanField(blank=True, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    chapter_code = models.CharField(max_length=30)

    section = models.ForeignKey(
        'Section', blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return "Chapter {0}".format(self.chapter_code)

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
        return 'chapter-%s' % self.pk

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
        return self.headings.all().order_by('heading_code')

    def get_headings_url(self):
        """
        Returns a chapter url to a view listing the child headings
        :return:
        """
        return reverse(
            'hierarchy-section-chapter-headings',
            kwargs={'chapter_code_2': self.chapter_code[:2]}
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'chapter-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)

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

        if hasattr(parent, 'section') and parent.section is not None:
            tree[level].append({"id": parent.section.id,
                                "description": parent.section.title,
                                "commodity_code": parent.section.roman_numeral,
                                "type": "section"
                                })

        # tree[level].append({"id": self.id,
        #                         "description": self.description,
        #                         "commodity_code": self.commodity_code,
        #                         "type": "chapter"})

        return tree

    # @staticmethod
    # def _append_descendant_data(parent, tree, level):
    #     """
    #     Appends a tree of descendants to the passed tree from passed parent
    #     :param parent: parent model instance
    #     :param tree: list of descendants
    #     :param level: int
    #     """
    #     print(parent, tree, level)
    #     try:
    #         children = parent.get_hierarchy_children()
    #         print(children)
    #         for child in children:
    #             # if type(child) is Commodity:
    #             if child.commodity_code not in ["9900000000", "9950000000", "9905000000"]:
    #                 tree[level].append({"id": child.id,
    #                                 "description": child.description,
    #                                 "commodity_code": child.commodity_code,
    #                                 "type": child._meta.model_name})
    #     except Exception as err:
    #         print(err.args)


class Heading(models.Model):
    goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    productline_suffix = models.CharField(max_length=2, null=True)
    leaf = models.BooleanField(blank=True, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    heading_code = models.CharField(max_length=10)
    heading_code_4 = models.CharField(
        max_length=4, null=True, blank=True
    )

    tts_json = models.TextField(blank=True, null=True)

    chapter = models.ForeignKey(
        'hierarchy.Chapter', blank=True, null=True, on_delete=models.CASCADE,
        related_name='headings'
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

    def get_regulations(self):
        """
        Returns a list of regulations instances either related to the commodity or it's parent subheading
        :return: queryset
        """
        regulations = list(self.regulation_set.all())

        # if self.parent_subheading:
        #     regulations + list(self.parent_subheading.regulation_set.all())

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
        groups = {}
        rules_of_origin = {
            "rules": [],
            "footnotes": []
        }
        for group_member in country.rulesgroupmember_set.all():
            for document in group_member.rules_group.rulesdocument_set.all():
                rules_of_origin['footnotes'] = document.footnotes.all().order_by('id')
                for rule in document.rule_set.all().order_by('id'):
                    if rule.chapter == self.chapter:
                        rules_of_origin['rules'].append(rule)
            group_name = group_member.rules_group.description
            groups[group_name] = rules_of_origin

        return groups

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'heading-%s' % self.pk

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
        kwargs = {'heading_code': self.heading_code_4 or self.heading_code}
        if country_code is not None:
            kwargs['country_code'] = country_code.lower()
        return reverse('heading-detail', kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [obj for obj in self.child_subheadings.all().order_by('commodity_code')]
        commodities = [obj for obj in self.children_concrete.all().order_by('commodity_code')]
        return sub_headings + commodities

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'heading-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)

    def update_content(self):
        """
        gets the Commodity content from the trade tariff service url as json response and stores it in the
        commodity's tts_json field

        """
        url = settings.HEADING_URL % self.heading_code

        resp = requests.get(url, timeout=10)
        resp_content = None

        if resp.status_code == 200:
            resp_content = resp.content.decode()
        elif resp.status_code == 404:
            url = settings.HEADING_URL % self.heading_code[:4]
            resp = requests.get(url, timeout=10)
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
        for idx, measure in enumerate(obj['import_measures']):
            measure['measure_id'] = idx
            for i, condition in enumerate(measure['measure_conditions']):
                if isinstance(condition, dict):
                    condition['measure_id'] = idx
                    condition['condition_id'] = i

        return json.dumps(obj)

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

        if hasattr(parent, 'chapter') and parent.chapter is not None:
            self.get_ancestor_data(parent.chapter, tree, level + 1)
            tree[level].append({"id": parent.chapter.id,
                             "description": parent.chapter.description,
                             "commodity_code": parent.chapter.commodity_code,
                             "type": "chapter"})
        elif hasattr(parent, 'section') and parent.section is not None:
            tree[level].append({"id": parent.section.id,
                                "description": parent.section.title,
                                "commodity_code": parent.section.roman_numeral,
                                "type": "section"
                                })

        # tree[level].append({"id": self.id,
        #                         "description": self.description,
        #                         "commodity_code": self.commodity_code,
        #                         "type": "heading"})

        return tree

    # @staticmethod
    # def _append_descendant_data(parent, tree, level):
    #     """
    #     Appends a tree of descendants to the passed tree from passed parent
    #     :param parent: parent model instance
    #     :param tree: list of descendants
    #     :param level: int
    #     """
    #     try:
    #         children = parent.get_hierarchy_children()
    #         for child in children:
    #             # if type(child) is Commodity:
    #             if child.commodity_code not in ["9900000000", "9950000000"]:
    #                 tree[level].append({"id": child.id,
    #                                 "description": child.description,
    #                                 "commodity_code": child.commodity_code,
    #                                 "type": child._meta.model_name})
    #     except Exception as err:
    #         logger.debug(err.args)


class SubHeading(models.Model):
    productline_suffix = models.CharField(max_length=2, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    commodity_code = models.CharField(max_length=10)  # goods_nomenclature_item_id
    goods_nomenclature_sid = models.CharField(max_length=10)

    tts_heading_json = models.TextField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'hierarchy.Heading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    parent_subheading = models.ForeignKey(
        'hierarchy.Subheading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('commodity_code', 'description')

    def __str__(self):
        return "Sub Heading {0}".format(self.commodity_code)

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'sub_heading-%s' % self.pk

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
        kwargs = {
            'node_id': 'sub_heading-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [obj for obj in self.child_subheadings.all().order_by('commodity_code')]
        commodities = [obj for obj in self.children_concrete.all().order_by('commodity_code')]
        return commodities + sub_headings

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

        if hasattr(parent, 'parent_subheading') and parent.parent_subheading is not None:
            self.get_ancestor_data(parent.parent_subheading, tree, level + 1)
            tree.insert(1, [{"id": parent.parent_subheading.id,
                             "description": parent.parent_subheading.description,
                             "commodity_code": parent.parent_subheading.commodity_code,
                             "type": "sub_heading"}])
        if hasattr(parent, 'heading') and parent.heading is not None:
            self.get_ancestor_data(parent.heading, tree, level + 1)
            tree[level].append({"id": parent.heading.id,
                             "description": parent.heading.description,
                             "commodity_code": parent.heading.commodity_code,
                             "type": "heading"})
        elif hasattr(parent, 'chapter') and parent.chapter is not None:
            self.get_ancestor_data(parent.chapter, tree, level + 1)
            tree[level].append({"id": parent.chapter.id,
                             "description": parent.chapter.description,
                             "commodity_code": parent.chapter.commodity_code,
                             "type": "chapter"})
        elif hasattr(parent, 'section') and parent.section is not None:
            tree[level].append({"id": parent.section.id,
                                "description": parent.section.title,
                                "commodity_code": parent.section.roman_numeral,
                                "type": "section"
                                })
        # else:
        #     self._append_descendant_data(self, tree, level)

        return tree

    # @staticmethod
    # def _append_descendant_data(parent, tree, level):
    #     """
    #     Appends a tree of descendants to the passed tree from passed parent
    #     :param parent: parent model instance
    #     :param tree: list of descendants
    #     :param level: int
    #     """
    #     tree[level].append({"id": parent.id,
    #                         "description": parent.description,
    #                         "commodity_code": parent.commodity_code,
    #                         "type": "sub_heading"})
