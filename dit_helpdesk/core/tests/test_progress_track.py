from core.models import ReloadDataTracking

from django.test import TestCase
from django.core.management import call_command

from datetime import datetime, timedelta


class ProgressTrackTestCase(TestCase):
    def setUp(self):
        ReloadDataTracking.objects.all().delete()

    def test_start_script(self):
        call_command("progress_track", "--start_reload_data")

        running_processes = ReloadDataTracking.objects.all()
        self.assertEqual(
            running_processes.count(),
            1,
        )

    def test_start_script_in_progress(self):
        ReloadDataTracking.objects.create(start_time=datetime.now())

        with self.assertRaises(RuntimeError) as in_progress_exception:
            call_command("progress_track", "--start_reload_data")

        exception_msg = str(in_progress_exception.exception)
        self.assertEqual(
            exception_msg,
            "Reload data script is already running, please wait a while before attempting the next run.",
        )

    def test_start_script_previous_exists(self):
        fake_start_time = datetime.now()
        fake_end_time = fake_start_time + timedelta(minutes=1)
        ReloadDataTracking.objects.create(
            start_time=fake_start_time, end_time=fake_end_time
        )

        call_command("progress_track", "--start_reload_data")

        running_processes = ReloadDataTracking.objects.all()
        self.assertEqual(
            running_processes.count(),
            2,
        )

    def test_end_script(self):
        ReloadDataTracking.objects.create(start_time=datetime.now())

        call_command("progress_track", "--end_reload_data")

        running_processes = ReloadDataTracking.objects.all()
        for process in running_processes:
            self.assertIsNotNone(process.end_time, "Test value should not be none.")

    def test_end_script_none_started(self):
        with self.assertRaises(RuntimeError) as not_running_exception:
            call_command("progress_track", "--end_reload_data")

        exception_msg = str(not_running_exception.exception)
        self.assertEqual(
            exception_msg,
            "Reload data script is not currently running.",
        )

    def test_end_script_multiple_started(self):
        ReloadDataTracking.objects.create(start_time=datetime.now())
        ReloadDataTracking.objects.create(start_time=datetime.now())

        with self.assertRaises(RuntimeError) as multiple_running_error:
            call_command("progress_track", "--end_reload_data")

        exception_msg = str(multiple_running_error.exception)
        self.assertEqual(
            exception_msg,
            "More than one reload data script is currently running, something has gone badly wrong",
        )

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
