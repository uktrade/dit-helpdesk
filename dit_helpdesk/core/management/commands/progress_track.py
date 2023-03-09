import logging

from core.models import ReloadDataTracking

from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--check_reload_data",
            action="store_true",
            help="Will print the current running status of reload_data scripts.",
        )

        parser.add_argument(
            "--check_timings",
            action="store_true",
            help="Shows the list of runtimes for all reload_data runs recorded in the DB.",
        )

    def handle(self, *args, **options):
        if options["check_reload_data"]:
            logger.info("Checking if reload_data is in progress")
            self.check_reload_data()

        elif options["check_timings"]:
            logger.info("Getting a full list of how long each run has taken")
            self.check_timings()

    def check_reload_data(self):
        running_processes = ReloadDataTracking.objects.filter(end_time__isnull=True)

        if running_processes.count() > 0:
            logger.info("Reload data script is already running")
            return True
        else:
            logger.info("Reload data script is not currently running.")
            return False

    def check_timings(self):
        processes = ReloadDataTracking.objects.all().order_by("start_time")
        for process in processes:
            start_time_readable = process.start_time.strftime("%d-%B-%Y")
            reason = process.reason
            print(str(start_time_readable) + " - " + str(reason))
            if process.end_time is None:
                process.end_time = timezone.now()
                process.save()

                for process in processes:
                    if process.run_time is None:
                        time_taken = process.end_time - process.start_time
                        process.run_time = time_taken
                        process.save()
                        logger.info(process.run_time)
                    else:
                        logger.info(process.run_time)
