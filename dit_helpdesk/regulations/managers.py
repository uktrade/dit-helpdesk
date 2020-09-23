from django.db import models


class RegulationGroupManager(models.Manager):
    def inherited(self, commodity_object):
        """Gets the regulation groups for the passed in object respecting inheritance.

        The commodity object will get all of its ancestor regulation groups returned
        as well as its own regulations groups.

        Example:
                            Heading A - <RegulationGroup: A>
                                        |
                        ------------------------------
                        |                              |
            Commodity A - <RegulationGroup: B>    Commodity B - No regulation group

            > RegulationGroup.object.inherited(<Heading A>)
            <Queryset: [RegulationGroup A]>

            > RegulationGroup.object.inherited(<Commodity A>)
            <Queryset: [RegulationGroup A, RegulationGroup B]>

            > RegulationGroup.object.inherited(<Commodity B>)
            <Queryset: [RegulationGroup A]>
        """
        regulation_groups = commodity_object.regulationgroup_set.all()

        parent = commodity_object.get_parent()
        if not parent:
            return regulation_groups

        parent_regulation_groups = self.inherited(commodity_object.get_parent())
        regulation_groups = regulation_groups.union(parent_regulation_groups)

        return regulation_groups
