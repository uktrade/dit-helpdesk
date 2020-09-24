import datetime as dt

from django.utils import timezone

from hierarchy.models import NomenclatureTree


def check_tree_freshness(max_delta=dt.timedelta(days=7)):
    current_tree = NomenclatureTree.get_active_tree()

    cutoff = timezone.now() - max_delta

    is_fresh = current_tree.start_date >= cutoff

    return is_fresh
