import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from hierarchy.helpers import delete_outdated_trees

from ...models import ReloadDataTracking, ReloadDataTrackingLockedError


logger = logging.getLogger(__name__)


class ReloadDataException(Exception):
    def __init__(self, step, error):
        self.step = step
        self.error = error
        super().__init__(self.error)

    def __str__(self):
        return f'"reload_data script has failed during the {self.step} step with the following error: {self.error}'


class Command(BaseCommand):
    def run_steps(self):
        try:
            # Collect static files (Django default)
            current_step = "collectstatic"
            logger.info(f"Start: {current_step}")
            call_command("collectstatic", "--noinput")
            logger.info(f"Completed: {current_step}")

            # Apply database migrations (Django default)
            current_step = "migrate"
            logger.info(f"Start: {current_step}")
            call_command("migrate")
            logger.info(f"Completed: {current_step}")

            # This pulls the initial data from the trade tariff service API and stores
            # the data in json files for future processing.
            # This will download the data for both the EU and the UK.
            current_step = "pull_api_update"
            logger.info(f"Start: {current_step}")
            call_command("pull_api_update")
            logger.info(f"Completed: {current_step}")

            # This takes the information downloaded from `pull_api_update` and transforms
            # it by building the correct parent/child relationships in the data and
            # removes any duplication. This information is stored in json files.
            current_step = "prepare_import_data"
            logger.info(f"Start: {current_step}")
            call_command("prepare_import_data")
            logger.info(f"Completed: {current_step}")

            # This prepares the data from the `prepare_import_data` step by converting
            # the json data into a csv format.
            current_step = "prepare_search_data"
            logger.info(f"Start: {current_step}")
            call_command("prepare_search_data")
            logger.info(f"Completed: {current_step}")

            # This creates the database instances of the nomenclature tree based on the
            # data gathered from `prepare_import_data`. This will generate the full
            # nomenclature trees for the UK and the EU. This doesn't activate the newly
            # created tree but generates it ready for it to be activated in other steps.
            current_step = "scrape_section_hierarchy"
            logger.info(f"Start: {current_step}")
            call_command("scrape_section_hierarchy")
            logger.info(f"Completed: {current_step}")

            # Imports the rules of origin into the database. The rules of origin files
            # are stored in an S3 bucket and this command will download these files and
            # produce rules of origin objects tied to the currently active nomenclature tree.
            # For docker environments an instance of Minio is used in place of connecting
            # to the S3 bucket.
            current_step = "import_rules_of_origin"
            logger.info(f"Start: {current_step}")
            call_command("import_rules_of_origin")
            logger.info(f"Completed: {current_step}")

            # This will link regulations that are attached to the previous nomenclature
            # tree to the new tree which is to be activated (which will have been generated
            # in other commands).
            current_step = "migrate_regulations"
            logger.info(f"Start: {current_step}")
            call_command("migrate_regulations")
            logger.info(f"Completed: {current_step}")

            # This generates the search keywords for the nomenclature tree.
            # Outputs the keywords into a csv file.
            current_step = "generate_search_keywords"
            logger.info(f"Start: {current_step}")
            call_command("generate_search_keywords", "--data_path=search/data")
            logger.info(f"Completed: {current_step}")

            # Imports the search data from `generate_search_keywords` into the database
            # models for the nomenclature tree.
            current_step = "import_search_keywords"
            logger.info(f"Start: {current_step}")
            call_command(
                "import_search_keywords",
                "--data_path=output/keywords_and_synonyms_merged.csv",
            )
            logger.info(f"Completed: {current_step}")

            # Creates a new search index for the most recent nomenclature tree and swaps
            # it out at the end.
            current_step = "swap_rebuild_index"
            logger.info(f"Start: {current_step}")
            call_command("swap_rebuild_index", "--keep-old-trees")
            logger.info(f"Completed: {current_step}")

            # Checks for any change to a countrys Trade Agreement Scenario and will update
            # this in the DB to reflect the new scenario.
            current_step = "update_scenarios"
            logger.info(f"Start: {current_step}")
            call_command("update_scenarios")
            logger.info(f"Completed: {current_step}")

            # Will delete data that is no longer needed now we have imported a new set.
            current_step = "clear_old_data"
            logger.info(f"Start: {current_step}")
            delete_outdated_trees()
            logger.info(f"Completed: {current_step}")
        except Exception as e:
            raise ReloadDataException(current_step, str(e)) from e

    def handle(self, **options):
        try:
            with ReloadDataTracking.lock():
                self.run_steps()
        except ReloadDataTrackingLockedError:
            raise CommandError("Already running reload data")
