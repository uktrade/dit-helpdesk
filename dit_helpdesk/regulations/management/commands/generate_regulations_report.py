from pathlib import Path

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, SubHeading

from ...models import RegulationGroup


ROOT_URL = "https://www.get-rules-tariffs-trade-with-uk.service.gov.uk"


def get_url(object, country_code):
    if isinstance(object, Section):
        return reverse(
            "section-detail",
            kwargs={"country_code": country_code, "section_id": object.pk},
        )
    elif isinstance(object, Chapter):
        return reverse(
            "chapter-detail",
            kwargs={
                "country_code": country_code,
                "chapter_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
            },
        )
    elif isinstance(object, Heading):
        return reverse(
            "heading-detail",
            kwargs={
                "country_code": country_code,
                "commodity_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
            },
        )
    elif isinstance(object, SubHeading):
        return reverse(
            "subheading-detail",
            kwargs={
                "country_code": country_code,
                "commodity_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
            },
        )
    elif isinstance(object, Commodity):
        return reverse(
            "commodity-detail",
            kwargs={
                "country_code": country_code,
                "commodity_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
            },
        )


def get_urls(objects, num_desired_urls, country_code):
    urls = []
    for obj in objects:
        if obj.leaf:
            urls.append(get_url(obj, country_code))

        if len(urls) >= num_desired_urls:
            return urls

    if len(urls) < num_desired_urls:
        for obj in objects:
            urls += get_urls(
                obj.get_hierarchy_children(), num_desired_urls, country_code
            )

            if len(urls) >= num_desired_urls:
                return urls

    return urls


class RegulationGroupProxy:
    def __init__(self, regulation_group, country_code):
        self.regulation_group = regulation_group
        self.country_code = country_code

    def __getattr__(self, attr):
        return getattr(self.regulation_group, attr)

    @property
    def example_urls(self):
        num_desired_urls = 5
        urls = []

        section_urls = get_urls(
            self.regulation_group.sections.all(), num_desired_urls, self.country_code
        )

        chapter_urls = get_urls(
            self.regulation_group.chapters.all(), num_desired_urls, self.country_code
        )

        heading_urls = get_urls(
            self.regulation_group.headings.all(), num_desired_urls, self.country_code
        )

        subheading_urls = get_urls(
            self.regulation_group.subheadings.all(), num_desired_urls, self.country_code
        )

        commodity_urls = get_urls(
            self.regulation_group.commodities.all(), num_desired_urls, self.country_code
        )

        url_groups = [
            section_urls,
            chapter_urls,
            heading_urls,
            subheading_urls,
            commodity_urls,
        ]
        while len(urls) < num_desired_urls and any(
            len(url_group) for url_group in url_groups
        ):
            for url_group in url_groups:
                try:
                    url = url_group.pop()
                except IndexError:
                    continue
                urls.append(url)
                if len(urls) >= num_desired_urls or all(
                    len(url_group) for url_group in url_groups
                ):
                    break

        return [ROOT_URL + url for url in urls]


class Command(BaseCommand):
    help = """Command to generate HTML files showing all regulations"""

    def add_arguments(self, parser):
        parser.add_argument("country_code", type=str)

    def handle(self, *args, **options):
        root_dir = Path("regulations")
        try:
            root_dir.mkdir()
        except FileExistsError:
            pass

        index_path = root_dir / Path("index.html")
        with index_path.open("w") as index_file:
            html = render_to_string(
                "regulations/report/index.html",
                {
                    "regulation_groups": (
                        RegulationGroupProxy(regulation_group, options["country_code"])
                        for regulation_group in RegulationGroup.objects.all()
                    )
                },
            )
            index_file.write(html)
