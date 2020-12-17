from reversion.admin import VersionAdmin

from django.contrib import admin

from .models import Regulation, RegulationGroup


@admin.register(RegulationGroup)
class RegulationGroupAdmin(VersionAdmin):
    pass


@admin.register(Regulation)
class RegulationAdmin(VersionAdmin):
    pass
