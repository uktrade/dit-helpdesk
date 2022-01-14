from core.models import ReloadDataTracking

from django.test import TestCase
from django.core.management import call_command

from datetime import datetime, timedelta


class ProgressTrackTestCase(TestCase):
    def test_check_script(self):
        fake_start_time = datetime.now()
        fake_end_time = fake_start_time + timedelta(minutes=1)
        ReloadDataTracking.objects.create(
            start_time=fake_start_time, end_time=fake_end_time
        )

        with self.assertLogs(
            "core.management.commands.progress_track", level="INFO"
        ) as output_log:
            call_command("progress_track", "--check_reload_data")

        self.assertIn(
            "Reload data script is not currently running.",
            str(output_log.output[1]),
        )

    def test_check_script_in_progress(self):
        ReloadDataTracking.objects.create(start_time=datetime.now())

        call_command("progress_track", "--check_reload_data")

        with self.assertLogs(
            "core.management.commands.progress_track", level="INFO"
        ) as output_log:
            call_command("progress_track", "--check_reload_data")

        self.assertIn(
            "Reload data script is already running",
            str(output_log.output[1]),
        )

    def test_timings_check(self):
        fake_start_time = datetime.now()
        fake_end_time = fake_start_time + timedelta(minutes=1)
        ReloadDataTracking.objects.create(
            start_time=fake_start_time, end_time=fake_end_time
        )

        with self.assertLogs(
            "core.management.commands.progress_track", level="INFO"
        ) as output_log:
            call_command("progress_track", "--check_timings")

        expected_time_taken = fake_end_time - fake_start_time
        self.assertIn(str(expected_time_taken), str(output_log.output[1]))
