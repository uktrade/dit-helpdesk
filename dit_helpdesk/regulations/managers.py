from django.db import models


class RegulationManager(models.Manager):
    def inherited(self, commodity_object):
        """Gets the regulation objects for the passed in object respecting inheritance.

        The commodity object will get all of its ancestor regulations returned as
        well as its own regulations.

        Example:
                            Heading A - <Regulation: A>
                                        |
                        ------------------------------
                        |                              |
            Commodity A - <Regulation: B>    Commodity B - No regulation

            > Regulation.object.inherited(<Heading A>)
            <Queryset: [Regulation A]>

            > Regulation.object.inherited(<Commodity A>)
            <Queryset: [Regulation A, Regulation B]>

            > Regulation.object.inherited(<Commodity B>)
            <Queryset: [Regulation A]>
        """
        regulations = commodity_object.regulation_set.all()

        parent = commodity_object.get_parent()
        if not parent:
            return regulations

        parent_regulations = self.inherited(commodity_object.get_parent())
        regulations = regulations.union(parent_regulations)

        return regulations
