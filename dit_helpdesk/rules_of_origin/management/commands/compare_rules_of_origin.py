import logging
import csv

from django.core.management.base import BaseCommand

from rules_of_origin.models import Rule, SubRule, RulesDocument, RulesDocumentFootnote


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--compare", action="store_true")
        parser.add_argument("--output", action="store_true")

    def handle(self, **options):
        if options["compare"]:
            self.compare()

        elif options["output"]:
            self.output_roo_csv()

    def output_roo_csv(self):
        # Go to the DB and collate the data for each rule, rule doc and rule footnote
        # dump it all into a csv that can then be compared to another
        # ./manage.py compare_rules_of_origin --output

        all_rules = Rule.objects.all()
        all_sub_rules = SubRule.objects.all()
        all_footnotes = RulesDocumentFootnote.objects.all()
        all_rules_docs = RulesDocument.objects.all()

        logger.critical("Got the following in each table:")
        logger.critical("Rules: " + str(len(all_rules)))
        logger.critical("Rules Documents: " + str(len(all_rules_docs)))
        logger.critical("Subrules: " + str(len(all_sub_rules)))
        logger.critical("Rule Footnotes: " + str(len(all_footnotes)))

        rules_csv_file = open("rules_of_origin_rules.csv", "w")
        with rules_csv_file:
            writer = csv.writer(rules_csv_file)
            logger.critical("Writing Rules Now")
            for rule in all_rules:
                rule_attribs = []
                for attrib in rule.__dict__:
                    if (
                        attrib not in "_state"
                        and attrib not in "hs_from"
                        and attrib not in "hs_to"
                    ):
                        rule_attribs.append(rule.__dict__[attrib])
                writer.writerow(rule_attribs)
            logger.critical("Finished Writing Rules")

        rules_doc_csv_file = open("rules_of_origin_rules_docs.csv", "w")
        with rules_doc_csv_file:
            writer = csv.writer(rules_doc_csv_file)
            logger.critical("Writing Rules Documents Now")
            for rule_doc in all_rules_docs:
                rule_doc_attribs = []
                for attrib in rule_doc.__dict__:
                    if attrib not in "_state":
                        rule_doc_attribs.append(rule_doc.__dict__[attrib])
                writer.writerow(rule_doc_attribs)
            logger.critical("Finished Writing Rules Documents")

        subrules_csv_file = open("rules_of_origin_subrules.csv", "w")
        with subrules_csv_file:
            writer = csv.writer(subrules_csv_file)
            logger.critical("Writing Subrules Now")
            for subrule in all_sub_rules:
                subrule_attribs = []
                for attrib in subrule.__dict__:
                    if attrib not in "_state":
                        subrule_attribs.append(subrule.__dict__[attrib])
                writer.writerow(subrule_attribs)
            logger.critical("Finished Writing Subrules")

        rules_footnotes_csv_file = open(
            "rules_of_origin_rules_document_footnotes.csv", "w"
        )
        with rules_footnotes_csv_file:
            writer = csv.writer(rules_footnotes_csv_file)
            logger.critical("Writing Footnotes Now")
            for footnote in all_footnotes:
                footnote_attribs = []
                for attrib in footnote.__dict__:
                    if attrib not in "_state":
                        footnote_attribs.append(footnote.__dict__[attrib])
                writer.writerow(footnote_attribs)
            logger.critical("Finished Writing Footnotes")

    def compare(self):
        # Take 2 csv files and compare the contents, output the differences.
        # ./manage.py compare_rules_of_origin --compare
        rules_doc_1 = "rules_of_origin_rules_orig.csv"
        rules_doc_2 = "rules_of_origin_rules.csv"
        with open(rules_doc_1, "r") as t1, open(rules_doc_2, "r") as t2:
            fileone = t1.readlines()
            filetwo = t2.readlines()
            logger.critical("Checking RULES Differences Now")
            for line in filetwo:
                if line not in fileone:
                    logger.critical(
                        "*****************************************************************"
                    )
                    logger.critical("LINE DIFFERENCE: ")
                    logger.critical(
                        "The following row does not match the original ROO data: "
                    )
                    logger.critical(line)
                    logger.critical(
                        "*****************************************************************"
                    )
            logger.critical("Finished Checking RULES Differences")

        rules_doc_doc_1 = "rules_of_origin_rules_docs_orig.csv"
        rules_doc_doc_2 = "rules_of_origin_rules_docs.csv"
        with open(rules_doc_doc_1, "r") as t1, open(rules_doc_doc_2, "r") as t2:
            fileone = t1.readlines()
            filetwo = t2.readlines()
            logger.critical("Checking RULES DOCUMENT Differences Now")
            for line in filetwo:
                if line not in fileone:
                    logger.critical(
                        "*****************************************************************"
                    )
                    logger.critical("LINE DIFFERENCE: ")
                    logger.critical(
                        "The following row does not match the original ROO data: "
                    )
                    logger.critical(line)
                    logger.critical(
                        "*****************************************************************"
                    )
            logger.critical("Finished Checking RULES DOCUMENT Differences")

        subrules_doc_1 = "rules_of_origin_subrules_orig.csv"
        subrules_doc_2 = "rules_of_origin_subrules.csv"
        with open(subrules_doc_1, "r") as t1, open(subrules_doc_2, "r") as t2:
            fileone = t1.readlines()
            filetwo = t2.readlines()
            logger.critical("Checking SUBRULES Differences Now")
            for line in filetwo:
                if line not in fileone:
                    logger.critical(
                        "*****************************************************************"
                    )
                    logger.critical("LINE DIFFERENCE: ")
                    logger.critical(
                        "The following row does not match the original ROO data: "
                    )
                    logger.critical(line)
                    logger.critical(
                        "*****************************************************************"
                    )
            logger.critical("Finished Checking SUBRULES Differences")

        rules_foot_doc_1 = "rules_of_origin_rules_document_footnotes_orig.csv"
        rules_foot_doc_2 = "rules_of_origin_rules_document_footnotes.csv"
        with open(rules_foot_doc_1, "r") as t1, open(rules_foot_doc_2, "r") as t2:
            fileone = t1.readlines()
            filetwo = t2.readlines()
            logger.critical("Checking FOOTNOTE Differences Now")
            for line in filetwo:
                if line not in fileone:
                    logger.critical(
                        "*****************************************************************"
                    )
                    logger.critical("LINE DIFFERENCE: ")
                    logger.critical(
                        "The following row does not match the original ROO data: "
                    )
                    logger.critical(line)
                    logger.critical(
                        "*****************************************************************"
                    )
            logger.critical("Finished Checking FOOTNOTE Differences")
