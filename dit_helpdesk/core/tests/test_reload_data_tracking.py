import datetime
import pytz

from freezegun import freeze_time
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from core.models import ReloadDataTracking, ReloadDataTrackingLockedError


class ReloadDataTrackingTestCase(TestCase):
    def test_creates_object_when_running(self):
        with freeze_time("2022-12-31 12:44") as frozen_datetime:
            with ReloadDataTracking.lock() as obj:
                self.assertEqual(ReloadDataTracking.objects.count(), 1)
                self.assertEqual(obj, ReloadDataTracking.objects.first())
                self.assertEqual(
                    obj.start_time,
                    datetime.datetime(2022, 12, 31, 12, 44, tzinfo=pytz.utc),
                )
                self.assertIsNone(obj.end_time)
                self.assertIsNone(obj.run_time)
                self.assertIsNone(obj.reason)
                frozen_datetime.tick(delta=datetime.timedelta(minutes=10))

        obj.refresh_from_db()
        self.assertEqual(ReloadDataTracking.objects.count(), 1)
        self.assertEqual(obj, ReloadDataTracking.objects.first())
        self.assertEqual(
            obj.start_time, datetime.datetime(2022, 12, 31, 12, 44, tzinfo=pytz.utc)
        )
        self.assertEqual(
            obj.end_time, datetime.datetime(2022, 12, 31, 12, 54, tzinfo=pytz.utc)
        )
        self.assertEqual(obj.run_time, datetime.timedelta(minutes=10))
        self.assertIsNone(obj.reason)

    def test_runs_code(self):
        to_run = Mock()
        with ReloadDataTracking.lock():
            to_run()

        to_run.assert_called_once()

    def test_blocks_parallel_runs(self):
        ReloadDataTracking.objects.create(start_time=timezone.now())

        to_run = Mock()
        with self.assertRaises(ReloadDataTrackingLockedError):
            with ReloadDataTracking.lock():
                to_run()

        to_run.assert_not_called()

    def test_runs_when_previous_run_completed(self):
        ReloadDataTracking.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + datetime.timedelta(minutes=1),
        )
        to_run = Mock()
        with ReloadDataTracking.lock():
            to_run()

        to_run.assert_called_once()

    def test_handles_exceptions(self):
        class MyException(Exception):
            pass

        with self.assertRaises(MyException) as cm:
            with freeze_time("2022-12-31 12:44") as frozen_datetime:
                with ReloadDataTracking.lock() as obj:
                    self.assertEqual(ReloadDataTracking.objects.count(), 1)
                    self.assertEqual(obj, ReloadDataTracking.objects.first())
                    self.assertEqual(
                        obj.start_time,
                        datetime.datetime(2022, 12, 31, 12, 44, tzinfo=pytz.utc),
                    )
                    self.assertIsNone(obj.end_time)
                    self.assertIsNone(obj.run_time)
                    self.assertIsNone(obj.reason)
                    frozen_datetime.tick(delta=datetime.timedelta(minutes=10))
                    raise MyException("This is my exception")

        self.assertEqual(str(cm.exception), "This is my exception")

        self.assertEqual(ReloadDataTracking.objects.count(), 1)
        obj = ReloadDataTracking.objects.first()
        self.assertEqual(obj, ReloadDataTracking.objects.first())
        self.assertEqual(
            obj.start_time, datetime.datetime(2022, 12, 31, 12, 44, tzinfo=pytz.utc)
        )
        self.assertEqual(
            obj.end_time, datetime.datetime(2022, 12, 31, 12, 54, tzinfo=pytz.utc)
        )
        self.assertEqual(obj.run_time, datetime.timedelta(minutes=10))
        self.assertEqual(obj.reason, "This is my exception")
