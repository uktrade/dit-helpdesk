import logging

from django.apps import apps
from django.test import TestCase

from hierarchy.models import SubHeading, Heading
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder, hierarchy_model_map

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class HierarchyBuilderTestCase(TestCase):
    """
    Test Hierarchy Importer
    """

    def test_file_loader(self):
        sections = HierarchyBuilder().file_loader(model_name="Section")
        self.assertTrue(isinstance(sections, list))
        self.assertTrue(set(["section_id" in item.keys() for item in sections]))

    def test_instance_builder_for_section(self):
        model_name = "Section"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance = builder.instance_builder(model, data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.section_id, 1)

    def test_instance_builder_for_chapter(self):
        chapter_model_name = "Chapter"
        chapter_data = HierarchyBuilder.file_loader(model_name=chapter_model_name)
        chapter_model = apps.get_model(app_label="hierarchy",
                                       model_name=chapter_model_name)

        # load section data
        section_model_name = "Section"
        section_data = HierarchyBuilder.file_loader(model_name=section_model_name)
        section_model = apps.get_model(app_label="hierarchy", model_name=section_model_name)

        builder = HierarchyBuilder()

        section_instance = builder.instance_builder(
            section_model,
            section_data[0]
        )

        self.assertTrue(isinstance(section_instance, section_model))
        self.assertEqual(section_instance.section_id, 1)

        section_model.objects.bulk_create([section_instance])
        chapter_instance = builder.instance_builder(chapter_model, chapter_data[0])

        self.assertTrue(isinstance(chapter_instance, chapter_model))
        self.assertEqual(chapter_instance.chapter_code, "0100000000")

    def test_instance_builder_for_heading(self):
        model_name = "Heading"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance_data = [item for item in data if item["goods_nomenclature_item_id"] == "2509000000"]
        instance = builder.instance_builder(model, instance_data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.heading_code, "2509000000")

    def test_instance_builder_for_subheading(self):
        model_name = "SubHeading"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance_data = [item for item in data if item["goods_nomenclature_item_id"] == "0204430000"]

        instance = builder.instance_builder(model, instance_data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.commodity_code, "0204430000")

    def test_instance_builder_for_commodity(self):
        model_name = "Commodity"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance_data = [item for item in data if item["goods_nomenclature_item_id"] == "2934999049"]
        instance = builder.instance_builder(model, instance_data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.commodity_code, "2934999049")

    def test_load_data_for_section(self):
        model_name = "Section"
        builder = HierarchyBuilder()
        builder.load_data(model_name)
        file_data = HierarchyBuilder().file_loader(model_name=model_name)
        self.assertEqual(builder.data[model_name]["data"], file_data)
        self.assertTrue(isinstance(builder.data[model_name]["data"], list))

    def test_lookup_parent_for_chapter(self):
        model_names = ["Section"]
        builder = HierarchyBuilder()

        for model_name in model_names:
            builder.load_data(model_name)

        parent_model_name = "Section"
        child_model_code = 27623
        parent_model = apps.get_model(app_label=hierarchy_model_map[parent_model_name]["app_name"],
                                      model_name=parent_model_name)
        for parent in builder.data[parent_model_name]["data"]:
            if child_model_code in parent['child_goods_nomenclature_sids']:
                parent_instance_data = builder.rename_key(parent, 'child_goods_nomenclature_sids', 'tts_json')
                parent_model.objects.create(**parent_instance_data)
        self.assertEqual(builder.lookup_parent(parent_model, "27623").section_id, 1)

    def test_lookup_parent_for_heading(self):
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder = HierarchyBuilder()

        for model_name in model_names:
            builder.load_data(model_name)

        parent_model_name = "Chapter"
        child_model_code = "0100000000"
        parent_model = apps.get_model(app_label=hierarchy_model_map[parent_model_name]["app_name"],
                                      model_name=parent_model_name)
        for parent in builder.data[parent_model_name]["data"]:
            if child_model_code == parent['goods_nomenclature_item_id']:
                parent_instance_data = builder.rename_key(parent, 'goods_nomenclature_item_id', 'chapter_code')
                parent_model.objects.create(**parent_instance_data)
        self.assertEqual(builder.lookup_parent(parent_model, "27623").description, "LIVE ANIMALS")

    def test_processed_orphan_subheadings(self):

        builder = HierarchyBuilder()
        all_subheadings = builder.file_loader("SubHeading")
        all_headings = builder.file_loader("Heading")
        all_chapters = builder.file_loader("Chapter")

        subheadings = [subheading for subheading in all_subheadings if
                       subheading["parent_goods_nomenclature_sid"] == all_subheadings[0]["goods_nomenclature_sid"]]
        parent_subheading_ids = [subheading["parent_goods_nomenclature_sid"] for subheading in subheadings]

        parent_subheadings = [subheading for subheading in all_subheadings if
                              subheading['goods_nomenclature_sid'] in parent_subheading_ids]
        parent_parent_subheading_ids = [parent_subheading["parent_goods_nomenclature_sid"]
                                        for parent_subheading in parent_subheadings]

        parent_parent_subheadings = [subheading for subheading in all_subheadings
                                     if subheading['goods_nomenclature_sid'] in parent_parent_subheading_ids]
        parent_heading_ids = [parent_subheading["parent_goods_nomenclature_sid"]
                              for parent_subheading in parent_parent_subheadings]

        parent_headings = [heading for heading in all_headings
                           if heading['goods_nomenclature_sid'] in [int(item) for item in parent_heading_ids]]
        parent_chapter_ids = [parent_heading["parent_goods_nomenclature_sid"]
                              for parent_heading in parent_headings]

        parent_chapters = [chapter for chapter in all_chapters if chapter['goods_nomenclature_sid'] in parent_chapter_ids]

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="Chapter")
        for chapter in parent_chapters:
            chapter = builder.rename_key(chapter, 'goods_nomenclature_item_id', 'chapter_code')
            model.objects.create(**chapter)

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="Heading")
        for heading in parent_headings:
            heading = builder.rename_key(heading, 'goods_nomenclature_item_id', 'heading_code')
            model.objects.create(**heading)

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="SubHeading")
        for parent_subheading in parent_parent_subheadings:
            parent_subheading = builder.rename_key(parent_subheading, 'goods_nomenclature_item_id', 'commodity_code')
            parent_subheading = builder.rename_key(parent_subheading, 'leaf', 'tts_is_leaf')
            model.objects.create(**parent_subheading)

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="SubHeading")
        for parent_subheading in parent_subheadings:
            parent_subheading = builder.rename_key(parent_subheading, 'goods_nomenclature_item_id', 'commodity_code')
            parent_subheading = builder.rename_key(parent_subheading, 'leaf', 'tts_is_leaf')
            model.objects.create(**parent_subheading)

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="SubHeading")
        for subheading in subheadings:
            subheading = builder.rename_key(subheading, 'goods_nomenclature_item_id', 'commodity_code')
            subheading = builder.rename_key(subheading, 'leaf', 'tts_is_leaf')
            model.objects.create(**subheading)
        self.assertFalse(builder.process_orphaned_subheadings())

