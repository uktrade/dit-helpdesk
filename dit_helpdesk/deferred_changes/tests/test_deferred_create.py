from django import forms
from django.test import RequestFactory, TestCase

from ..forms import DeferredFormMixin

from .models import ChildModel, OtherModel, ParentModel


class OtherModelForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        fields = ["name"]
        model = OtherModel


class ParentModelForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        fields = ["others"]
        model = ParentModel


class ChildModelForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        fields = ["parent"]
        model = ChildModel


class DeferredCreateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_non_related_model(self):
        request = self.factory.post("/", data={"name": "bar"})
        form = OtherModelForm(request.POST)

        deferred_create = form.defer_create()
        self.assertFalse(OtherModel.objects.exists())

        deferred_changes = list(deferred_create.get_deferred_changes())
        self.assertEqual(len(deferred_changes), 1)
        deferred_change = deferred_changes[0]
        self.assertEqual(deferred_change.description, "Name")
        self.assertTrue(deferred_change.single_value)
        self.assertEqual(deferred_change.value, "bar")

        deferred_create.apply()
        obj = OtherModel.objects.get()
        self.assertEqual(obj.name, "bar")

    def test_foreign_key_related_model(self):
        parent = ParentModel.objects.create(name="parent")

        request = self.factory.post("/", data={"parent": parent.pk})
        form = ChildModelForm(request.POST)

        deferred_create = form.defer_create()
        self.assertFalse(ChildModel.objects.exists())

        deferred_changes = list(deferred_create.get_deferred_changes())
        self.assertEqual(len(deferred_changes), 1)
        deferred_change = deferred_changes[0]
        self.assertEqual(deferred_change.description, "Parent")
        self.assertTrue(deferred_change.single_value)
        self.assertEqual(deferred_change.value, str(parent))

        deferred_create.apply()
        obj = ChildModel.objects.get()
        self.assertEqual(obj.parent, parent)

    def test_many_to_many(self):
        a_other = OtherModel.objects.create(name="a")
        b_other = OtherModel.objects.create(name="b")

        request = self.factory.post("/", data={"others": [a_other.pk, b_other.pk]})
        form = ParentModelForm(request.POST)

        deferred_create = form.defer_create()
        self.assertFalse(ParentModel.objects.exists())

        deferred_changes = list(deferred_create.get_deferred_changes())
        self.assertEqual(len(deferred_changes), 1)
        deferred_change = deferred_changes[0]
        self.assertEqual(deferred_change.description, "Others")
        self.assertFalse(deferred_change.single_value)
        self.assertEqual(list(deferred_change.values), [str(a_other), str(b_other)])

        deferred_create.apply()
        obj = ParentModel.objects.get()
        self.assertIn(a_other, obj.others.all())
        self.assertIn(b_other, obj.others.all())
