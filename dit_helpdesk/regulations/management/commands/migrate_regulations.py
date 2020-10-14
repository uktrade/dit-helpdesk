from django.core.management.base import BaseCommand

from django.conf import settings

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    help = (
        """Command to migrate regulations from a previous NomenclatureTree to the current one"""
    )

    def handle(self, *args, **options):
        self.stdout.write("Migrating regulations..")

        with process_swapped_tree():
            new_tree = NomenclatureTree.get_active_tree()
            prev_tree = NomenclatureTree.objects.filter(
                region=settings.PRIMARY_REGION,
                start_date__lt=new_tree.start_date
            ).latest('start_date')

            self.stdout.write(f"New tree: {new_tree}")
            self.stdout.write(f"Previous tree: {prev_tree}")

            regulation_groups = prev_tree.regulationgroup_set.all()
            new_tree.regulationgroup_set.set(regulation_groups)

            regulations = prev_tree.regulation_set.all()
            new_tree.regulation_set.set(regulations)
            new_tree.save()

        self.stdout.write("Done!")
