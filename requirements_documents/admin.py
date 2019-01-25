from django.contrib import admin

from .models import (
    Section, Chapter, Heading,
    Commodity, HasRequirementDocument, RequirementDocument, AbstractCommodity,
    EuTradeHelpdeskDocument, EuTradeHelpdeskDocumentTitle, CommodityHasDocTitle
)

admin.site.register(Section)
admin.site.register(Chapter)
admin.site.register(Heading)
admin.site.register(Commodity)
admin.site.register(HasRequirementDocument)
admin.site.register(RequirementDocument)
admin.site.register(EuTradeHelpdeskDocument)
admin.site.register(EuTradeHelpdeskDocumentTitle)
admin.site.register(CommodityHasDocTitle)
admin.site.register(AbstractCommodity)