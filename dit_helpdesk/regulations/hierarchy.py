from django.db.models import QuerySet

from hierarchy.models import Heading


def promote_regulations(commodity_object):
    """Descends down a commodity tree from the passed in object and promotes regulation objects back up the tree.

    The end result should be that any regulation objects that could be picked up
    via inheritance are promoted.

    This means that a commodity object with all of its children having the same
    regulation attached will have that regulation promoted to itself and
    then removed from that child object itself.

    Example:
        Before:
                       Heading - No regulation
                                 |
                   ------------------------------
                  |                              |
        Commodity - <Regulation: A>    Commodity - <Regulation: A>
                    <Regulation: B>

        After:
                       Heading - <Regulation: A>
                                 |
                   ------------------------------
                  |                              |
        Commodity - <Regulation: B>    Commodity - No regulation
    """
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


def get_regulations(commodity_object) -> QuerySet:
    """ Gets the regulation objects for the passed in object respecting inheritance.

    The commodity object will get all of its ancestor regulations returned as
    well as its own regulations.

    Example:
                        Heading A - <Regulation: A>
                                    |
                    ------------------------------
                    |                              |
        Commodity A - <Regulation: B>    Commodity B - No regulation

        > get_regulation(<Heading A>)
        <Queryset: [Regulation A]>

        > get_regulation(<Commodity A>)
        <Queryset: [Regulation A, Regulation B]>

        > get_regulation(<Commodity B>)
        <Queryset: [Regulation A]>
    """
    regulations = commodity_object.regulation_set.all()

    parent = commodity_object.get_parent()
    if not parent:
        return regulations

    parent_regulations = get_regulations(commodity_object.get_parent())
    regulations = regulations.union(parent_regulations)

    return regulations
