import logging

from django.apps import apps
from django.test import TestCase

from trade_tariff_service.importer import HierarchyBuilder, hierarchy_model_map

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
        model_name = "Chapter"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance = builder.instance_builder(model, data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.chapter_code, "0100000000")

    def test_instance_builder_for_heading(self):
        model_name = "Heading"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance = builder.instance_builder(model, data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.heading_code, "0101000000")

    def test_instance_builder_for_subheading(self):
        model_name = "SubHeading"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance = builder.instance_builder(model, data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.commodity_code, "0101000000")

    def test_instance_builder_for_commodity(self):
        model_name = "Commodity"
        data = HierarchyBuilder.file_loader(model_name=model_name)
        model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

        builder = HierarchyBuilder()
        instance = builder.instance_builder(model, data[0])
        self.assertTrue(isinstance(instance, model))
        self.assertEqual(instance.commodity_code, "0101210000")

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
            # logger.debug(parent['child_goods_nomenclature_sids'])
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
        subheadings = builder.file_loader("SubHeading")

        headings = builder.file_loader("Heading")

        heading_data = headings[4]
        heading_data = builder.rename_key(heading_data, 'goods_nomenclature_item_id', 'heading_code')

        model = apps.get_model(app_label=hierarchy_model_map["Heading"]["app_name"], model_name="Heading")
        heading = model.objects.create(**heading_data)

        child_data = subheadings[1]
        child_data = builder.rename_key(child_data, 'goods_nomenclature_item_id', 'commodity_code')
        child_data = builder.rename_key(child_data, 'leaf', 'tts_is_leaf')

        parent_data = subheadings[0]
        parent_data = builder.rename_key(parent_data, 'goods_nomenclature_item_id', 'commodity_code')
        parent_data = builder.rename_key(parent_data, 'leaf', 'tts_is_leaf')

        model = apps.get_model(app_label=hierarchy_model_map["SubHeading"]["app_name"], model_name="SubHeading")

        model.objects.create(**child_data)
        parent_data['heading_id'] = heading.pk
        model.objects.create(**parent_data)

        self.assertEqual(builder.process_orphaned_subheadings(), 1)

    # @staticmethod
    # def test_get_section_data_from_api():
    #     builder = HierarchyBuilder()
    #     builder.get_section_data_from_api()
