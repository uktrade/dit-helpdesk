from hierarchy.models import Heading


def promote_regulations(commodity_object):
    regulations_to_promote = None
    for child in commodity_object.get_hierarchy_children():
        promote_regulations(child)
        regulations_to_promote = child.regulation_set.all()

    if not regulations_to_promote:
        return

    commodity_object.regulation_set.add(*regulations_to_promote)

    for child in commodity_object.get_hierarchy_children():
        child.regulation_set.remove(*regulations_to_promote)
