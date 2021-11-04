import logging

from core.models import ReloadDataTracking

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--start_reload_data",
            action="store_true",
            help="""Registers to the DB that a reload_data script is now running.
                WARNING: Do not start manually unless testing specifically.""",
        )

        parser.add_argument(
            "--end_reload_data",
            action="store_true",
            help="""Registers to the DB that the running reload_data script has completed.
                Only use manually when acknowledging an error which has been dealt with.""",
        )

        parser.add_argument(
            "--reason",
            type=str,
            help="""Used with end_reload_data, string to detail reason for ending script progress.""",
        )

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

        if options["start_reload_data"]:
            logger.info("Tracking the start of the reload_data script.")
            self.start_reload_data()

        elif options["end_reload_data"]:
            logger.info("Tracking the completion of the reload_data script.")
            try:
                self.end_reload_data(options["reason"])
            except ValueError:
                raise CommandError("Provide a reason for ending the reload_data script")

        elif options["check_reload_data"]:
            logger.info("Checking if reload_data is in progress")
            self.check_reload_data()

        elif options["check_timings"]:
            logger.info("Getting a full list of how long each run has taken")
            self.check_timings()

    def start_reload_data(self):
        is_already_running = self.check_reload_data()

        if is_already_running is True:
            logger.info("Cancelling reload_data")
            raise RuntimeError(
                "Reload data script is already running, please wait a while before attempting the next run."
            )
        else:
            logger.info("Registering the current reload_data process")
            ReloadDataTracking.objects.create(start_time=datetime.now())

    def end_reload_data(self, reason):
        running_processes = ReloadDataTracking.objects.filter(end_time__isnull=True)

        if running_processes.count() > 1:
            raise RuntimeError(
                "More than one reload data script is currently running, something has gone badly wrong"
            )
        elif running_processes.count() == 0:
            raise RuntimeError("Reload data script is not currently running.")
        else:
            logger.info("Registering the current reload_data process as complete")
            for completed_process in running_processes:
                completed_process.end_time = datetime.now()
                completed_process.reason = reason
                completed_process.save()

    def check_reload_data(self):
        running_processes = ReloadDataTracking.objects.filter(end_time__isnull=True)

        if running_processes.count() > 0:
            logger.info("Reload data script is already running")
            return True
        else:
            logger.info("Reload data script is not currently running.")
            return False

    def check_timings(self):
        processes = ReloadDataTracking.objects.all()

        for process in processes:
            if process.run_time is None:
                time_taken = process.end_time - process.start_time
                process.run_time = time_taken
                process.save()
                logger.info(process.run_time)
            else:
                logger.info(process.run_time)
