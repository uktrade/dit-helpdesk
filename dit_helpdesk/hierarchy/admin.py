from django.contrib import admin

from hierarchy.models import Section, Chapter, Heading, SubHeading

admin.site.register(Section)
admin.site.register(Chapter)
admin.site.register(Heading)
admin.site.register(SubHeading)
