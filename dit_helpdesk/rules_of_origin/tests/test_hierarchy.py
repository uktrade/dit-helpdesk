import logging

from django.test import TestCase
from mixer.backend.django import mixer

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, SubRule, Rule

from rules_of_origin.hierarchy import get_rules_of_origin

from countries.models import Country

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class GetRulesOfOriginTestCase(TestCase):
    """
    Test the realtime get_rules_of_origin function
    coverage run manage.py test dit_helpdesk/rules_of_origin/tests/test_hierarchy.py --settings=config.settings.test
    """

    def setUp(self):
        # Setup which can be used across all/multiple tests
        self.country = mixer.blend(
            Country,
            country_code="KA",
            # alternative_non_trade_country_code="",
            name="The Hyborian Kingdom Of Aquilonia",
            # has_eu_trade_agreement="",
            trade_agreement_title="Fealty Demands Of King Conan",
            trade_agreement_type="Trade and cooperation agreement",
            is_eu=False,
            scenario="TRADE_AGREEMENT",
            # content_url="",
        )

        self.rulesdocument = mixer.blend(
            RulesDocument,
            countries=[self.country],
            description=mixer.RANDOM,
        )

        self.footnote = mixer.blend(
            RulesDocumentFootnote,
            number=1,
            identifier="001",
            link_html="",
            note=mixer.RANDOM,
            rules_document=self.rulesdocument,
        )

        self.intro_note = mixer.blend(
            RulesDocumentFootnote,
            number=2,
            identifier="COMM",
            link_html="",
            note=mixer.RANDOM,
            rules_document=self.rulesdocument,
        )

        self.rule_text_footnote = "This is rule text used to test footnotes [001]"

        self.commodity_code_heading_level = "0123000000"
        self.commodity_code = "0123456789"

        self.alt_chapter_code = "0223456789"
        self.alt_heading_code = "0122456789"
        self.alt_subheading_code = "0123496789"

    def create_rules(self, rules_to_build):
        # Factory function to create a rule

        # Instantiate the rules dict
        self.test_rules = {}
        for rule_to_build in rules_to_build:
            self.test_rules[rule_to_build] = []

        for rule_to_build in rules_to_build:
            # Decide on rule values
            if "Chapter" in rule_to_build:
                code_input = f"{rule_to_build} 01"
                hs_from_input = "01"
                hs_type_input = "CH"
            elif "Heading" in rule_to_build:
                code_input = "0123"
                hs_from_input = "0123"
                hs_type_input = "PO"
            elif "Subheading" in rule_to_build:
                code_input = "0123.45"
                hs_from_input = "012345"
                hs_type_input = "PO"

            if "ex" in rule_to_build:
                extract_indicator = True
            else:
                extract_indicator = False

            # Build rule
            self.test_rules[rule_to_build].append(
                mixer.blend(
                    Rule,
                    code=code_input,
                    description=mixer.RANDOM,
                    is_extract=extract_indicator,
                    rules_document=self.rulesdocument,
                    rule_text=mixer.RANDOM,
                    rule_text_processed=self.rule_text_footnote,
                    hs_from=hs_from_input,
                    hs_to=None,
                    hs_type=hs_type_input,
                )
            )

    def check_footnotes(self, roo_data):
        # Many tests in the file check the footnotes returned contain the
        # setUp footnotes, so this private function will do that job for them

        returned_footnotes = roo_data[self.rulesdocument.description]["footnotes"]
        self.assertIn(self.footnote, returned_footnotes)
        self.assertEqual(len(returned_footnotes), 1)

        returned_intro_notes = roo_data[self.rulesdocument.description][
            "introductory_notes"
        ]
        self.assertEqual(self.intro_note, returned_intro_notes)

    def check_roo_list(self, code_to_check, expected_rules_list, expected_count):
        # Tests need to perform the same basic checks; how many rules do we expect
        # and which ones do we expect to be present in the result.

        roo_data = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=code_to_check,
        )

        if roo_data:
            returned_rules = roo_data[self.rulesdocument.description]["rules"]
            self.assertEqual(len(returned_rules), expected_count)

        for rule in expected_rules_list:
            self.assertIn(rule, returned_rules)

        # Return roo_data in case the test wants to use the data further
        return roo_data

    def test_scenario_chapter_rule(self):
        """
        Test - Single chapter (2 digit) level rule

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - No rule
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>       Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Chapter"])

        # Check that one rule is returned by the function which matches the test rule
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["Chapter"], 1
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Expect headings matching the chapter code to also contain the rule
        roo_data = self.check_roo_list(
            self.commodity_code_heading_level, self.test_rules["Chapter"], 1
        )
        # Expect codes under other chapters to get no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_multiple_chapter_rules(self):
        """
        Test - Multiple chapter (2 digit) level rules

        Heirarchy:
        Chapter     - Rule 1, Rule 2
           |
        Heading     - No rule
           |
        Subheading  - No rule

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>           Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Chapter", "Chapter"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Chapter"][0], self.test_rules["Chapter"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

    def test_scenario_heading_rule(self):
        """
        Test - Single heading (4 digit) level rule

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>       Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Heading"])

        # Check that one rule is returned by the function which matches the test rule
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["Heading"], 1
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Assert a commodity under a different heading does not get the rule
        self.check_roo_list(self.alt_heading_code, [], 0)
        # Expect codes under other chapters to get no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_multiple_heading_rules(self):
        """
        Test - Multiple heading (4 digit) level rules

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1, Rule 2
           |
        Subheading  - No rule

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>          Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Heading", "Heading"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Heading"][0], self.test_rules["Heading"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

    def test_scenario_subheading_rule(self):
        """
        Test - Single subheading (6 digit) level rule

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - No rule
           |
        Subheading  - Rule 1

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>       Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading"])

        # Check that one rule is returned by the function which matches the test rule
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["Subheading"], 1
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Assert a commodity under a different subheading does not get the rule
        self.check_roo_list(self.alt_subheading_code, [], 0)

    def test_scenario_multiple_subheading_rules(self):
        """
        Test - Multiple subheading (6 digit) level rules

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - No rule
           |
        Subheading  - Rule 1, Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>           Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading", "Subheading"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Subheading"][0], self.test_rules["Subheading"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

    def test_scenario_chapter_heading_rule_mix(self):
        """
        Test - Rules at chapter (2 digit) and heading (4 digit) levels

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - Rule 2
           |
        Subheading  - No rule

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>           Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Heading", "Chapter"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Chapter"][0], self.test_rules["Heading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Expect other headings to only get the chapter level rule
        self.check_roo_list(self.alt_heading_code, self.test_rules["Chapter"], 1)
        # Expect codes outside the chapter to get no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_chapter_subheading_rule_mix(self):
        """
        Test - Rules at chapter (2 digit) and subheading (6 digit) levels

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - No rule
           |
        Subheading  - Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>           Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading", "Chapter"])

        # Test outcome of a code linked to a rule at chapter and a rule at subheading level
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Chapter"][0], self.test_rules["Subheading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Expect other headings to only get the chapter level rule
        self.check_roo_list(self.alt_heading_code, self.test_rules["Chapter"], 1)
        # Expect codes outside the chapter to get no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_heading_subheading_mix(self):
        """
        Test - Rules at heading (4 digit) and subheading (6 digit) levels

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>           Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading", "Heading"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["Heading"][0], self.test_rules["Subheading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Expect another subheading under the same heading to contain the heading level rule only
        self.check_roo_list(self.alt_subheading_code, self.test_rules["Heading"], 1)
        # Expect a commodity under a different heading to have no rules attached
        self.check_roo_list(self.alt_heading_code, [], 0)

    def test_scenario_all_levels_mix(self):
        """
        Test - Rules at chapter (2 digit), heading (4 digit) and subheading (6 digit) levels

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - Rule 2
           |
        Subheading  - Rule 3

        Document:
                                                                            Country
                                                                               |
                                                                          Rule Document
                                                                               |
                   _______________________________________________________________________________________________________________________________
                  |                              |                             |                              |                                   |
        Rule 1 - <ex: False>             Rule 2 - <ex: False>          Rule 3 - <ex: False>      Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading", "Heading", "Chapter"])

        # Check that both rules are returned by the function which match the test rules
        roo_data = self.check_roo_list(
            self.commodity_code,
            [
                self.test_rules["Chapter"][0],
                self.test_rules["Heading"][0],
                self.test_rules["Subheading"][0],
            ],
            3,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Expect another subheading under the same heading to contain the heading and chapter level rules
        self.check_roo_list(
            self.alt_subheading_code,
            [self.test_rules["Chapter"][0], self.test_rules["Heading"][0]],
            2,
        )
        # Expect a heading sharing the same chapter code to return only the chapter level rule
        self.check_roo_list(self.alt_heading_code, self.test_rules["Chapter"], 1)
        # Expect a commodity under another chapter to contain no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_ranged_rule(self):
        """
        Test - Single rule applying to a commodity code range

        Heirarchy:
                          Chapter - No rule
                                 |
                          Heading - No rule
                                 |
                   ______________________________
                  |                              |
        Subheading - Rule 1             Subheading - Rule 1

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>       Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Subheading"])

        # Amend rule created above to apply across a range of subheading level codes
        self.test_rules["Subheading"][0].code = "0123.45 to 0123.50"
        self.test_rules["Subheading"][0].hs_from = "012345"
        self.test_rules["Subheading"][0].hs_to = "012350"
        self.test_rules["Subheading"][0].save()

        # Check that the rule is returned by a code in the range
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["Subheading"], 1
        )
        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Check a different code in the range also returns the rule
        roo_data = self.check_roo_list(
            self.alt_subheading_code, self.test_rules["Subheading"], 1
        )
        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Check that a code outside the range does not return the rule
        self.check_roo_list("0123100000", [], 0)

    def test_scenario_extract_chapter_subheading_mix(self):
        """
        Test - Extract rule at subheading (6 digit) level and chapter (2 digit) level - PO and CH level

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - No rule
           |
        Subheading  - Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: True>           Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Subheading", "ex Chapter"])

        # Test outcome of a code with an Extract rule at chapter and subheading level
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Chapter"][0], self.test_rules["ex Subheading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different subheading only returns the chapter level rule
        self.check_roo_list(self.alt_subheading_code, self.test_rules["ex Chapter"], 1)
        # Ensure a rule under a different heading only returns the chapter level rule
        self.check_roo_list(self.alt_heading_code, self.test_rules["ex Chapter"], 1)
        # Ensure a rule under a different chapter returns no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_extract_chapter_heading_mix(self):
        """
        Test - Extract rule at heading level (4 digit) and chapter (2 digit) level - PO and CH level

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - Rule 2
           |
        Subheading  - No rule

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: True>            Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Heading", "ex Chapter"])

        # Test outcome of a code with an Extract rule at chapter and heading level
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Chapter"][0], self.test_rules["ex Heading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different heading only returns the chapter level rule
        self.check_roo_list(self.alt_heading_code, self.test_rules["ex Chapter"], 1)
        # Ensure a rule under a different chapter returns no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_extract_heading_subheading_mix(self):
        """
        Test - Extract rule at subheading (6 digit) and heading (4 digit) level - both PO level

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: True>            Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Heading", "ex Subheading"])

        # Test outcome of a code with an Extract rule at subheading and heading level
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Subheading"][0], self.test_rules["ex Heading"][0]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different subheading only returns the heading level rule
        self.check_roo_list(self.alt_subheading_code, self.test_rules["ex Heading"], 1)
        # Ensure a rule under a different heading returns no rules
        self.check_roo_list(self.alt_heading_code, [], 0)

    def test_scenario_extract_subheading_rule(self):
        """
        Test - Extract rule at subheading (6 digit) level only - single PO level

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - No rule
           |
        Subheading  - Rule 1

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: True>        Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Subheading"])

        # Test outcome of a code with an Extract rule at subheading level only
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["ex Subheading"], 1
        )
        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different subheading returns no rules
        self.check_roo_list(self.alt_subheading_code, [], 0)

    def test_scenario_extract_heading_rule(self):
        """
        Test - Extract rule at heading (4 digit) level only - single PO level

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: True>        Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Heading"])

        # Test outcome of a code with an Extract rule at heading level only
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["ex Heading"], 1
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different heading returns no rules
        self.check_roo_list(self.alt_heading_code, [], 0)

    def test_scenario_extract_chapter_rule(self):
        """
        Test - Extract rule at chapter (2 digit) level only - single CH level

        Heirarchy:
        Chapter     - Rule 1
           |
        Heading     - No rule
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: True>       Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Chapter"])

        # Test outcome of a code with an Extract rule at chapter level only
        roo_data = self.check_roo_list(
            self.commodity_code, self.test_rules["ex Chapter"], 1
        )
        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different heading returns no rules
        self.check_roo_list(self.alt_chapter_code, [], 0)

    def test_scenario_regular_and_extract_rules(self):
        """
        Test - Extract rule and regular rule apply to a single commodity

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - No rule
           |
        Subheading  - Rule 1, Rule 2

        Document:
                                                              Country
                                                                 |
                                                            Rule Document
                                                                 |
                   ____________________________________________________________________________________________
                  |                              |                            |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: False>       Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Subheading", "Subheading"])
        # Test outcome of a code with an Extract rule and a regular rule at the same level
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Subheading"][0], self.test_rules["Subheading"][0]],
            2,
        )
        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a rule under a different heading returns no rules
        self.check_roo_list(self.alt_subheading_code, [], 0)

    def test_scenario_extract_ranged_overlap_with_single(self):
        """
        Test - Extract rule and ranged Extract rule for a single commodity code

        Heirarchy:
                             Chapter - No rule
                                    |
                             Heading - No rule
                                    |
                   ___________________________________
                  |                                   |
        Subheading - Rule 1, Rule 2             Subheading - Rule 1

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: True>           Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Subheading", "ex Subheading"])

        # Amend rule created above to apply across a range of subheading level codes
        self.test_rules["ex Subheading"][0].code = "0123.45 to 0123.50"
        self.test_rules["ex Subheading"][0].hs_from = "012345"
        self.test_rules["ex Subheading"][0].hs_to = "012350"
        self.test_rules["ex Subheading"][0].save()

        self.test_rules["ex Subheading"][1].code = "0123.45"
        self.test_rules["ex Subheading"][1].hs_from = "012345"
        self.test_rules["ex Subheading"][1].save()

        # Test outcome of a code with an ranged Extract rule and a second extract rule within the range
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Subheading"][0], self.test_rules["ex Subheading"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a code under the range doesn't display the single rule
        self.check_roo_list(
            self.alt_subheading_code, [self.test_rules["ex Subheading"][0]], 1
        )

        # Ensure a code outside the subheading range doesn't display any rules
        self.check_roo_list("0123996789", [], 0)

    def test_scenario_extract_rule_ranges_overlap(self):
        """
        Test - Two Extract rules applying to an overlapping range of codes apply for a single commodity

        Heirarchy:
                                         Chapter - No rule
                                                |
                                         Heading - No rule
                                                |
                  ____________________________________________________________
                 |                              |                             |
        Subheading - Rule 1       Subheading - Rule 1, Rule 2        Subheading - Rule 2

        Document:
                                                             Country
                                                                |
                                                           Rule Document
                                                                |
                   _________________________________________________________________________________________________
                  |                              |                                 |                                |
        Rule 1 - <ex: True>             Rule 2 - <ex: True>           Footnote - <identifier:"001">       Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Subheading", "ex Subheading"])

        # Amend rule created above to apply across a range of subheading level codes
        self.test_rules["ex Subheading"][0].code = "0123.45 to 0123.50"
        self.test_rules["ex Subheading"][0].hs_from = "012345"
        self.test_rules["ex Subheading"][0].hs_to = "012350"
        self.test_rules["ex Subheading"][0].save()

        self.test_rules["ex Subheading"][1].code = "0123.48 to 0123.55"
        self.test_rules["ex Subheading"][1].hs_from = "012348"
        self.test_rules["ex Subheading"][1].hs_to = "012355"
        self.test_rules["ex Subheading"][1].save()

        # Test outcome of a code with an ranged Extract rule and a second extract rule within the range
        roo_data = self.check_roo_list(
            self.alt_subheading_code,
            [self.test_rules["ex Subheading"][0], self.test_rules["ex Subheading"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a code under the first range doesn't display the second rule
        self.check_roo_list(
            self.commodity_code, [self.test_rules["ex Subheading"][0]], 1
        )

        # Ensure a code under the second range doesn't display the first rule
        self.check_roo_list("0123546789", [self.test_rules["ex Subheading"][1]], 1)

        # Ensure a code outside the subheading range doesn't display any rules
        self.check_roo_list("0123996789", [], 0)

    def test_scenario_duplicate_rule_for_heading_subheading(self):
        """
        Test - The same extract rule applies to a heading (4 digit) and a subheading beneath it (6 digit)

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - Rule 1

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: True>       Footnote - <identifier:"001">      Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["ex Heading", "ex Heading"])

        # Amend rule created above to apply across a heading and one of its subheadings seperately
        self.test_rules["ex Heading"][1].hs_from = "012345"
        self.test_rules["ex Heading"][1].save()

        # A rule covered by the heading code and the subheading code within range will contain the rule twice
        roo_data = self.check_roo_list(
            self.commodity_code,
            [self.test_rules["ex Heading"][0], self.test_rules["ex Heading"][1]],
            2,
        )

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.check_footnotes(roo_data)

        # Ensure a code under the first range doesn't display the second
        self.check_roo_list(
            self.alt_subheading_code, [self.test_rules["ex Heading"][0]], 1
        )

        # Ensure a code under the first range doesn't display the second
        self.check_roo_list(
            self.commodity_code_heading_level, [self.test_rules["ex Heading"][0]], 1
        )

        # Ensure a code outside the range returns no rules
        self.check_roo_list(self.alt_heading_code, [], 0)

        # Note: This case can be removed when this is confirmed to be a data error

    def test_scenario_mutliple_rule_docs(self):
        """
        Test - Multiple rules documents (GSP countries with trade agreements example)

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1, Rule 2
           |
        Subheading  - No rule

        Document:
                                                                                                 Country
                                                                                                    |
                                                  _________________________________________________________________________________________________
                                                 |                                                                                                 |
                                            Rule Document 1                                                                                   Rule Document 2
                                                 |                                                                                                 |
                   ____________________________________________________________                                      ____________________________________________________________
                  |                              |                             |                                    |                              |                             |
        Rule 1 - <ex: False>        Footnote - <identifier:"001">    Footnote - <identifier:"COMM">         Rule 2 - <ex: False>        Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Heading", "Heading"])

        # Create the second rules document
        self.rulesdocument_2 = mixer.blend(
            RulesDocument,
            countries=[self.country],
            description=mixer.RANDOM,
        )
        self.footnote_2 = mixer.blend(
            RulesDocumentFootnote,
            number=1,
            identifier="001",
            link_html="",
            note=mixer.RANDOM,
            rules_document=self.rulesdocument_2,
        )
        self.intro_note_2 = mixer.blend(
            RulesDocumentFootnote,
            number=2,
            identifier="COMM",
            link_html="",
            note=mixer.RANDOM,
            rules_document=self.rulesdocument_2,
        )

        # Amend second rule to apply to second rule document
        self.test_rules["Heading"][1].rules_document = self.rulesdocument_2
        self.test_rules["Heading"][1].save()

        # Get the RoO data - we expect 2 sets of data returned, we want to check each seperate one.
        roo_data = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=self.commodity_code,
        )

        # Check we have 2 rule documents returned
        self.assertEquals(len(roo_data), 2)

        # Split the data into the expected 2 sets
        doc_1_rules = roo_data[self.rulesdocument.description]["rules"]
        doc_2_rules = roo_data[self.rulesdocument_2.description]["rules"]

        # Test that each doc has only one rule, and that rule is one of the 2 setup above.
        self.assertEqual(len(doc_1_rules), 1)
        self.assertEqual(len(doc_2_rules), 1)
        self.assertIn(self.test_rules["Heading"][0], doc_1_rules)
        self.assertIn(self.test_rules["Heading"][1], doc_2_rules)

        # Ensure the footnote and introductory notes are also returned and match those
        # established in the setUp
        self.assertIn(
            self.footnote, roo_data[self.rulesdocument.description]["footnotes"]
        )
        self.assertIn(
            self.footnote_2, roo_data[self.rulesdocument_2.description]["footnotes"]
        )
        self.assertEqual(
            self.intro_note,
            roo_data[self.rulesdocument.description]["introductory_notes"],
        )
        self.assertEqual(
            self.intro_note_2,
            roo_data[self.rulesdocument_2.description]["introductory_notes"],
        )

    def test_scenario_rule_doc_in_future(self):
        """
        Test - Rule document start date is in the future

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>       Footnote - <identifier:"001">     Footnote - <identifier:"COMM">

        """  # noqa: E501

        self.create_rules(["Heading"])

        # Set rule document start date way into future
        self.rulesdocument.start_date = "2500-01-01"
        self.rulesdocument.save()

        # Test result when the start date indicated in the rules doc is in the future
        # We should get nothing back
        self.check_roo_list(self.commodity_code, [], 0)

    def test_scenario_no_footnotes(self):
        """
        Test - Missing footnotes for a related rule

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1
           |
        Subheading  - No rule

        Document:
             Country
                |
            Rule Document
                |
        Rule 1 - <ex: False>

        """  # noqa: E501

        self.create_rules(["Heading"])

        # Remove all footnotes on a rule document
        self.footnote.delete()
        self.intro_note.delete()

        # Test outcome when there are no footnotes at all in rules document
        with self.assertRaises(
            RulesDocumentFootnote.DoesNotExist
        ) as missing_note_error:
            get_rules_of_origin(
                country_code=self.country.country_code,
                commodity_code=self.commodity_code,
            )

        exception_msg = str(missing_note_error.exception)
        self.assertEqual(
            exception_msg,
            "Missing expected footnotes for this commodity code",
        )

    def test_scenario_missing_introductory_notes(self):
        """
        Test - Missing introductory notes

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1, Rule 2
           |
        Subheading  - No rule

        Document:
                              Country
                                 |
                            Rule Document
                                 |
                   ______________________________
                  |                              |
        Rule 1 - <ex: True>          Footnote - <identifier:"001">

        """  # noqa: E501

        self.create_rules(["Heading"])

        # Remove the introductory note footnote
        self.intro_note.delete()

        # Test the error in the event of missing introductory notes
        with self.assertLogs("rules_of_origin.hierarchy", level="ERROR") as error_log:
            get_rules_of_origin(
                country_code=self.country.country_code,
                commodity_code=self.commodity_code,
            )

        self.assertIn(
            "Could not find introductory notes for KA - The Hyborian Kingdom Of Aquilonia - TRADE_AGREEMENT",
            str(error_log.output[0]),
        )

    def test_scenario_subrule(self):
        """
        Test - Rule document contains a subrule

        Heirarchy:
        Chapter     - No rule
           |
        Heading     - Rule 1, Subrule 1
           |
        Subheading  - No rule

        Document:
                                              Country
                                                 |
                                            Rule Document
                                                 |
                   ____________________________________________________________
                  |                              |                             |
        Rule 1 - <ex: False>      Footnote - <identifier:"001">     Footnote - <identifier:"COMM">
                  |
              Subrule 1

        """  # noqa: E501

        self.create_rules(["Heading"])

        self.subrule = mixer.blend(
            SubRule,
            rule=self.test_rules["Heading"][0],
            order="001",
            description=mixer.RANDOM,
            description_processed=mixer.RANDOM,
            rule_text=mixer.RANDOM,
            alt_rule_text=mixer.RANDOM,
            rule_text_processed=self.rule_text_footnote,
            alt_rule_text_processed=mixer.RANDOM,
        )

        # Test to ensure Subrule is included if present in rules document
        roo_data = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=self.commodity_code,
        )

        returned_rule = roo_data[self.rulesdocument.description]["rules"]

        for rule in returned_rule:
            subrules = rule.subrules.all()
            self.assertIn(self.subrule, subrules)
