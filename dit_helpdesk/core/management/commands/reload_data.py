import logging

from contextlib import contextmanager

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from hierarchy.helpers import delete_outdated_trees

from ...models import ReloadDataTracking, ReloadDataTrackingLockedError


logger = logging.getLogger(__name__)

@contextmanager
def logged_step(step_name):
    """
    Context manager to log a named step.
    """
    logger.info(f"Start: {current_step}")
    yield
    logger.info(f"Completed: {current_step}" )

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
            with logged_step("collectstatic"):
                call_command("collectstatic", "--noinput")

            # Apply database migrations (Django default)
            with logged_step("migrate"):
                call_command("migrate")

            # This pulls the initial data from the trade tariff service API and stores
            # the data in json files for future processing.
            # This will download the data for both the EU and the UK.
            with logged_step("pull_api_update"):
                call_command("pull_api_update")

            # This takes the information downloaded from `pull_api_update` and transforms
            # it by building the correct parent/child relationships in the data and
            # removes any duplication. This information is stored in json files.
            with logged_step("prepare_import_data"):
                call_command("prepare_import_data")

            # This prepares the data from the `prepare_import_data` step by converting
            # the json data into a csv format.
            with logged_step("prepare_search_data"):
            logger.info(f"Completed: {current_step}")

            # This creates the database instances of the nomenclature tree based on the
            # data gathered from `prepare_import_data`. This will generate the full
            # nomenclature trees for the UK and the EU. This doesn't activate the newly
            # created tree but generates it ready for it to be activated in other steps.
            with logged_step("scrape_section_hierarchy"):
                call_command("scrape_section_hierarchy")

            # Imports the rules of origin into the database. The rules of origin files
            # are stored in an S3 bucket and this command will download these files and
            # produce rules of origin objects tied to the currently active nomenclature tree.
            # For docker environments an instance of Minio is used in place of connecting
            # to the S3 bucket.
            with logged_step("import_rules_of_origin"):
                call_command("import_rules_of_origin")

            # This will link regulations that are attached to the previous nomenclature
            # tree to the new tree which is to be activated (which will have been generated
            # in other commands).
            with logged_step("migrate_regulations"):
                call_command("migrate_regulations")

            # This generates the search keywords for the nomenclature tree.
            # Outputs the keywords into a csv file.
            with logged_step("generate_search_keywords"):
                call_command("generate_search_keywords", "--data_path=search/data")

            # Imports the search data from `generate_search_keywords` into the database
            # models for the nomenclature tree.
            with logged_step("import_search_keywords"):
                call_command(
                    "import_search_keywords",
                    "--data_path=output/keywords_and_synonyms_merged.csv",
                )

            # Creates a new search index for the most recent nomenclature tree and swaps
            # it out at the end.
            with logged_step("swap_rebuild_index"):
                call_command("swap_rebuild_index", "--keep-old-trees")


            # Checks for any change to a countrys Trade Agreement Scenario and will update
            # this in the DB to reflect the new scenario.
            with logged_step("update_scenarios"):
                call_command("update_scenarios")

            # Will delete data that is no longer needed now we have imported a new set.
            with logged_step("clear_old_data"):
                delete_outdated_trees()
        except Exception as e:
            raise ReloadDataException(current_step, str(e)) from e

    def handle(self, **options):
        try:
            with ReloadDataTracking.lock():
                self.run_steps()
        except ReloadDataTrackingLockedError:
            raise CommandError("Already running reload data")
