def promote_regulation_groups(commodity_object):
    """Descends down a commodity tree from the passed in object and promotes regulation groups back up the tree.

    The end result should be that any regulation group objects that could be picked up
    via inheritance are promoted.

    This means that a commodity object with all of its children having the same
    regulation group attached will have that regulation group promoted to itself and
    then removed from those children.

    Example:
        Before:
                       Heading - No regulation group
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>
                    <RegulationGroup: B>

        After:
                       Heading - <RegulationGroup: A>
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: B>    Commodity - No regulation group
    """
    regulation_groups_to_promote = None
    for child in commodity_object.get_hierarchy_children():
        promote_regulation_groups(child)

        child_regulations = child.regulationgroup_set.all()
        if regulation_groups_to_promote is None:
            regulation_groups_to_promote = child_regulations
        else:
            regulation_groups_to_promote = regulation_groups_to_promote.intersection(
                child_regulations
            )

    if not regulation_groups_to_promote:
        return

    commodity_object.regulationgroup_set.add(*regulation_groups_to_promote)

    for child in commodity_object.get_hierarchy_children():
        child.regulationgroup_set.remove(*regulation_groups_to_promote)


def replicate_regulation_groups(commodity_object, regulation_groups_to_replicate=None):
    """Descends down a commodity tree from the passed in object and replicates regulation groups down the tree.

    The end result should be that any regulation group objects that are in a parent commodity object are replicated
    down through its ancestors.

    Example:
        Before:
                       Heading - <RegulationGroup: A>
                                 <RegulationGroup: B>
                                 |
                   ------------------------------
                  |                              |
        Commodity - No regulation groups    Commodity - No regulations groups

        After:
                       Heading - <RegulationGroup: A>
                                 <RegulationGroup: B>
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>
                    <RegulationGroup: B>                <RegulationGroup: B>
    """
    if regulation_groups_to_replicate:
        commodity_object.regulationgroup_set.add(*regulation_groups_to_replicate)

    for child in commodity_object.get_hierarchy_children():
        replicate_regulation_groups(child, commodity_object.regulationgroup_set.all())
