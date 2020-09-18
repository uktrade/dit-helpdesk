import sys
import logging

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from hierarchy.models import Section, Chapter, Heading, SubHeading
from commodities.models import Commodity

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


test_hierarchy_model_map = {
    "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
}


test_hierarchy_model_map_modified = {
    "Commodity": {"file_name": "test_subsets_modified/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "test_subsets_modified/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "test_subsets_modified/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "test_subsets_modified/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "test_subsets_modified/sections.json", "app_name": "hierarchy"},
}


class ScrapeSectionHierarchyTest(TestCase):

    def test_command_output(self):

        with patch(
                'trade_tariff_service.HierarchyBuilder.hierarchy_model_map',
                test_hierarchy_model_map):
            call_command('scrape_section_hierarchy', activate_new_tree=True, stdout=sys.stdout)

        for region in ('EU', 'UK'):
            self.assertTrue(Section.get_active_objects(region).exists())
            self.assertEquals(Section.get_active_objects(region).count(), 21)
    
            self.assertTrue(Chapter.get_active_objects(region).exists())
            self.assertEquals(Chapter.get_active_objects(region).count(), 97)
    
            self.assertTrue(Heading.get_active_objects(region).exists())
            self.assertEquals(Heading.get_active_objects(region).count(), 371)
    
            self.assertTrue(SubHeading.get_active_objects(region).exists())
            self.assertEquals(SubHeading.get_active_objects(region).count(), 76)
    
            self.assertTrue(Commodity.get_active_objects(region).exists())
            self.assertEquals(Commodity.get_active_objects(region).count(), 84)
    
            # spot check that the test data hierarchy was properly populated
            c1 = Commodity.get_active_objects(region).get(goods_nomenclature_sid=36150)
            self.assertEquals(c1.commodity_code, "2849200000")
            self.assertEquals(c1.description, "Of silicon")
    
            sh1 = c1.parent_subheading
            self.assertEquals(sh1.commodity_code, "2849000000")
            self.assertEquals(sh1.description, "Carbides, whether or not chemically defined")
    
            h1 = sh1.heading
            self.assertEquals(h1.commodity_code, "2843000000")
            self.assertEquals(h1.description, "VI. MISCELLANEOUS")
    
            ch1 = h1.chapter
            self.assertEquals(ch1.chapter_code, "2800000000")
            self.assertEquals(
                ch1.description,
                "INORGANIC CHEMICALS; ORGANIC OR INORGANIC COMPOUNDS OF PRECIOUS METALS, "
                "OF RARE-EARTH METALS, OF RADIOACTIVE ELEMENTS OR OF ISOTOPES"
            )
    
            s1 = ch1.section
            self.assertEquals(s1.roman_numeral, "VI")
            self.assertEquals(s1.title, "Products of the chemical or allied industries")

    def test_subsequent_run(self):
        with patch(
                'trade_tariff_service.HierarchyBuilder.hierarchy_model_map',
                test_hierarchy_model_map):
            call_command('scrape_section_hierarchy', activate_new_tree=True, stdout=sys.stdout)

        with patch(
                'trade_tariff_service.HierarchyBuilder.hierarchy_model_map',
                test_hierarchy_model_map_modified):
            call_command('scrape_section_hierarchy', activate_new_tree=True, stdout=sys.stdout)

        for region in ('EU', 'UK'):
    
            self.assertTrue(Section.get_active_objects(region).exists())
            self.assertEquals(Section.get_active_objects(region).count(), 21)
    
            self.assertTrue(Chapter.get_active_objects(region).exists())
            self.assertEquals(Chapter.get_active_objects(region).count(), 97)
    
            self.assertTrue(Heading.get_active_objects(region).exists())
            self.assertEquals(Heading.get_active_objects(region).count(), 371)
    
            self.assertTrue(SubHeading.get_active_objects(region).exists())
            self.assertEquals(SubHeading.get_active_objects(region).count(), 76)
    
            self.assertTrue(Commodity.get_active_objects(region).exists())
            self.assertEquals(Commodity.get_active_objects(region).count(), 84)
    
            # spot check that the test data hierarchy was properly populated
            c1 = Commodity.get_active_objects(region).get(goods_nomenclature_sid=36150)
            self.assertEquals(c1.commodity_code, "2849200000")
            self.assertEquals(c1.description, "Of silicon (UPDATED)")
    
            sh1 = c1.parent_subheading
            self.assertEquals(sh1.commodity_code, "2849000000")
            self.assertEquals(
                sh1.description, "Carbides, whether or not chemically defined (UPDATED)")
    
            h1 = sh1.heading
            self.assertEquals(h1.commodity_code, "2843000000")
            self.assertEquals(h1.description, "VI. MISCELLANEOUS (UPDATED)")
    
            ch1 = h1.chapter
            self.assertEquals(ch1.chapter_code, "2800000000")
            self.assertEquals(
                ch1.description,
                "INORGANIC CHEMICALS; ORGANIC OR INORGANIC COMPOUNDS OF PRECIOUS METALS, "
                "OF RARE-EARTH METALS, OF RADIOACTIVE ELEMENTS OR OF ISOTOPES (UPDATED)"
            )
    
            s1 = ch1.section
            self.assertEquals(s1.roman_numeral, "VI")
            self.assertEquals(s1.title, "Products of the chemical or allied industries (UPDATED)")
