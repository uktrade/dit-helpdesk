import json
import os

from django.conf import settings

ROO_FP = os.path.join(
    settings.BASE_DIR, 'rules_of_origin/management/commands/roo_chile.json'
)
RULES_OF_ORIGIN_DATA = json.loads(open(ROO_FP).read())

'''
example commodities with rules of origin:

0403103900
0403101300
0403101900
0403103100
0403103300
1106309080
1106100000
0901110000
0901120000
0910911000
'''


def get_rules_of_origin_html_fragments(commodity):
    """
    For a given commodity, get the relevant ROO html fragments.

    TODO: this isn't country-specific, it gets the same data regardless
    of the user's selected country
    """
    heading = commodity.get_heading()
    chapter_code = heading.chapter.chapter_code[:2]
    chapter_headings = heading.chapter.headings.all()

    roo_keys = [
        'chapter__' + chapter_code, 'chapter_exclusion__' + chapter_code
    ]
    # include any entries relating to headings under the chapter
    for _heading in chapter_headings:
        roo_keys.append('heading__'+_heading.heading_code[:4])
        roo_keys.append('heading_exclusion__'+_heading.heading_code[:4])

    roo_fragments = []
    for key in roo_keys:
        if key in RULES_OF_ORIGIN_DATA:
            for html_fragment in RULES_OF_ORIGIN_DATA[key]:
                html_fragment = html_fragment.replace(
                    '<td class="table" valign="top">',
                    '<td class="govuk-table__cell app-table__cell">'
                )
                roo_fragments.append(html_fragment)

    return roo_fragments
