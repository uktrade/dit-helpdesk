from django.test import TestCase
from mixer.backend.django import mixer

from feedback.models import Feedback


class FeedbackModelTestCase(TestCase):

    """
    Test Models
    """

    def setUp(self):
        self.feedback = mixer.blend(Feedback)

    def test_feedback_model_str(self):
        self.assertEquals(
            str(self.feedback),
            "Form {0}".format(self.feedback.created_on.strftime("%B %d, %Y, %H:%M:%S")),
        )
