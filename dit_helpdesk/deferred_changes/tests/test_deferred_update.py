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


class DeferredUpdateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_non_related_model(self):
        obj = OtherModel.objects.create(name="foo")

        request = self.factory.post("/", data={"name": "bar"})
        form = OtherModelForm(request.POST, instance=obj)

        deferred_update = form.defer_update()
        self.assertEqual(obj.name, "foo")

        deferred_update.apply()
        self.assertEqual(obj.name, "bar")

    def test_foreign_key_related_model(self):
        parent = ParentModel.objects.create(name="parent")
        obj = ChildModel.objects.create()

        request = self.factory.post("/", data={"parent": parent.pk})
        form = ChildModelForm(request.POST, instance=obj)

        deferred_update = form.defer_update()
        self.assertEqual(obj.parent, None)

        deferred_update.apply()
        self.assertEqual(obj.parent, parent)

    def test_many_to_many(self):
        a_other = OtherModel.objects.create(name="a")
        b_other = OtherModel.objects.create(name="b")

        obj = ParentModel.objects.create(name="c")

        request = self.factory.post("/", data={"others": [a_other.pk, b_other.pk]})
        form = ParentModelForm(request.POST, instance=obj)

        deferred_update = form.defer_update()
        self.assertFalse(obj.others.exists())

        deferred_update.apply()
        self.assertIn(a_other, obj.others.all())
        self.assertIn(b_other, obj.others.all())
