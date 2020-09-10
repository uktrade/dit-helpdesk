from hierarchy.models import Heading


def promote_regulations(commodity_object):
    regulations_to_promote = None
    for child in commodity_object.get_hierarchy_children():
        promote_regulations(child)

        child_regulations = set(child.regulation_set.all())
        if regulations_to_promote is None:
            regulations_to_promote = child_regulations
        else:
            regulations_to_promote = regulations_to_promote & child_regulations

    if not regulations_to_promote:
        return

    commodity_object.regulation_set.add(*regulations_to_promote)

    for child in commodity_object.get_hierarchy_children():
        child.regulation_set.remove(*regulations_to_promote)


def get_regulations(commodity_object):
    regulations = set(commodity_object.regulation_set.all())

    parent = commodity_object.get_parent()
    if not parent:
        return regulations

    regulations |= get_regulations(commodity_object.get_parent())

    return regulations
