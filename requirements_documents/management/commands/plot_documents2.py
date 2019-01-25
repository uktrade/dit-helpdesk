from collections import defaultdict
import re

from django.core.management.base import BaseCommand, CommandError
import plotly.plotly as py
import plotly.graph_objs as go

from requirements_documents.models import Section, Commodity, RequirementDocument, HasRequirementDocument
from requirements_documents.models import EuTradeHelpdeskDocument, EuTradeHelpdeskDocumentTitle, CommodityHasDocTitle


NETWORK_INFO_JS = 'var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;'

TAG_NAME_REGEX = re.compile('^<[/]?(.*?)[/]?>.*', flags=re.MULTILINE | re.DOTALL)

LIMIT = 4000


def get_section_commodities(section_id):

    commodities = []

    section = Section.objects.get(section_id=section_id)
    for chapter in section.chapter_set.all():
        chapter_headings = []
        for heading in chapter.heading_set.all():
            chapter_headings.append(heading)
        chapter_headings = [o.pk for o in chapter_headings]
        commodities.extend(
            Commodity.objects.filter(heading_id__in=chapter_headings)
        )
    return commodities


def get_section_coords(section_id, y_offset):

    commodities = get_section_commodities(section_id)

    x_vals, y_vals, annotations = [], [], []

    max_y, curr_y = 0, y_offset
    commodity_positions = {}
    for c_obj in commodities[:LIMIT]:
        x_vals.append(100)
        y_vals.append(curr_y)
        annotations.append('commodity:%s %s' % (c_obj.pk, c_obj.commodity_code))
        commodity_positions[c_obj.pk] = (100, curr_y)
        if curr_y > max_y:
            max_y = curr_y
        curr_y += 10

    commodity_pks = [o.pk for o in commodities][:LIMIT]
    doc_title_rels = CommodityHasDocTitle.objects.filter(
        commodity__in=commodity_pks, origin_country='AL').select_related('document_title')
    document_titles = set([rel.document_title for rel in doc_title_rels])
    document_positions = {}

    if not document_titles:
        exit('no document rels found!')

    curr_y = y_offset + round(curr_y / 2)
    for doc in document_titles:
        x_vals.append(500)
        y_vals.append(curr_y)
        annotations.append('document_title:%s %s' % (doc.pk, doc.title))
        document_positions[doc.pk] = (500, curr_y)
        if curr_y > max_y:
            max_y = curr_y
        curr_y += 160

    # -------------------------------------------------------------
    # N = 1000

    x_edges, y_edges = [], []

    for rel in doc_title_rels:
        commodity_coord = commodity_positions[rel.commodity.pk]
        document_coord = document_positions[rel.document_title.pk]
        x_edges.append(
            tuple([commodity_coord[0], document_coord[0], None])
        )
        y_edges.append(
            tuple([commodity_coord[1], document_coord[1], None])
        )
        #edge_trace2['x'] += tuple([commodity_coord[0], document_coord[0], None])
        #edge_trace2['y'] += tuple([commodity_coord[1], document_coord[1], None])

    return x_vals, y_vals, x_edges, y_edges, annotations, y_offset
    #return node_trace2, edge_trace2, max_y


COUNTRY_CODES = ["AF", "CH", "BZ", "KP", "CN", "AL"]

invalid_titles = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52, 53, 54, 55, 63, 64, 60, 59, 58, 50]

import random
from selenium.webdriver import Firefox
from pprint import pprint
import time


def get_document_table():
    '''

    # this is used to spot check results

    driver = Firefox()
    titles_by_pk = {o.pk: o.title for o in EuTradeHelpdeskDocumentTitle.objects.all()}
    sections = [o for o in Section.objects.all()]
    all_commodities = []
    for section in sections:
        section_commodities = get_section_commodities(section.section_id)
        commodities_by_pk = {o.pk: o for o in section_commodities}
        section_commodities = [o.pk for o in section_commodities]
        all_commodities.extend(section_commodities)

    all_commodities = [o.pk for o in all_commodities]
    for country_code in COUNTRY_CODES[:2]:
        for title_pk in invalid_titles: #titles_by_pk.keys():  #
            rels = CommodityHasDocTitle.objects.filter(
                document_title=title_pk, origin_country=country_code,
                commodity_id__in=all_commodities)
            if rels.count() == 0:
                continue
            rels = [r for r in rels]
            # commodity_titles = {}
            # for rel in rels:
            #     if rel.document_title_id not in commodity_titles:
            #         commodity_titles[rel.document_title_id] = rel.document_title.title
            # print('\nall section titles:')
            # print('--------------------')
            # pprint(commodity_titles)
            # print('--------------------')

            random.shuffle(rels)
            for rel in rels[:7]:
                commodity_pk = rel.commodity_id
                commodity_code = commodities_by_pk[commodity_pk].commodity_code
                commodity_url = 'http://trade.ec.europa.eu/tradehelp/myexport#?product=%s&partner=AF&reporter=GB&tab=2' % commodity_code
                driver.get('https://google.com')
                driver.get(commodity_url)

                rels2 = CommodityHasDocTitle.objects.filter(
                    origin_country=country_code, commodity_id=commodity_pk
                )
                for rel2 in rels2:
                    print(str(rel2.document_title.pk) + ' - ' + rel2.document_title.title)
                import pdb; pdb.set_trace()

    exit()
    '''

    rows = []
    for section in Section.objects.all():
        commodities = get_section_commodities(section.section_id)
        commodity_pks = [o.pk for o in commodities]
        commodity_by_pk = {o.pk: o for o in commodities}

        for country_code in COUNTRY_CODES:

            rels = CommodityHasDocTitle.objects.filter(
                commodity_id__in=commodity_pks, origin_country=country_code
            ).select_related('document_title')

            rels_by_commodity = defaultdict(list)
            for rel in rels:
                rels_by_commodity[rel.commodity_id].append(rel)
            for commodity_id, commodity_doc_rels in rels_by_commodity.items():
                commodity_obj = commodity_by_pk[commodity_id]
                doc_titles = ' | '.join(
                    sorted([r.document_title.title for r in commodity_doc_rels])
                )
                curr_row = [
                    section.section_id, commodity_obj.commodity_code, country_code, doc_titles
                ]
                rows.append(curr_row)

    rows.sort(key=lambda row: row[:2])

    # check changes in document titles column
    '''
    prev_row = None
    for curr_row in rows:
        if prev_row is None:
            prev_row = curr_row
            continue
        if prev_row[-1] != curr_row[-1]:
            pass #import pdb; pdb.set_trace()
            #print()
        prev_row = curr_row
    import pdb; pdb.set_trace()
    '''

    # print('\n--------------------------\n'.join(sorted([o.title for o in EuTradeHelpdeskDocumentTitle.objects.all()])))

    title_country_counts = {}
    for section in Section.objects.all():
        section_commodities = get_section_commodities(section.section_id)
        section_commodities = [o.pk for o in section_commodities]
        for title_obj in EuTradeHelpdeskDocumentTitle.objects.all():
            for country_code in COUNTRY_CODES:
                count = CommodityHasDocTitle.objects.filter(
                    document_title=title_obj, origin_country=country_code,
                    commodity_id__in=section_commodities
                ).count()
                title_country_counts[(section.section_id, country_code, title_obj.pk)] = count
    titles_by_pk = {o.pk: o.title for o in EuTradeHelpdeskDocumentTitle.objects.all()}

    section_country_title = []
    for (k, v) in title_country_counts.items():
        if v == 0:
            continue
        section_id, country_code, title_pk = k
        if title_pk in invalid_titles:
            continue
        title = str(title_pk) + ' - ' + titles_by_pk[title_pk]
        section_country_title.append(
            [section_id, country_code, title]
        )
    section_country_title.sort(key=lambda tup: tup[:2])

    write_csv(
        '/Users/rossrochford/code/DIT/trade-helpdesk/trade-helpdesk/python/helpdesk_django/requirements_documents/management/commands/section_country_title.csv',
        section_country_title
    )



import csv


def write_csv(filepath, rows):
    with open(filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            csv_writer.writerow(row)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        get_document_table()

        exit()
        #section_id = options['section_id']
        ALL_x_vals, ALL_y_vals, ALL_x_edges, ALL_y_edges, ALL_annotations = [], [], [], [], []
        y_offset = 0
        section_count = 0
        for section in Section.objects.all():
            if section.id in (7, 10):
                continue
            tup = get_section_coords(section.id, y_offset+5000)
            x_vals, y_vals, x_edges, y_edges, annotations, y_offset = tup

            ALL_x_vals.extend(x_vals)
            ALL_y_vals.extend(y_vals)
            ALL_x_edges.extend(x_edges)
            ALL_y_edges.extend(y_edges)
            ALL_annotations.extend(annotations)
            section_count += 1
            if section_count > 3:
                break

        # Create a trace
        node_trace2 = go.Scatter(
            x=ALL_x_vals, y=ALL_y_vals, mode='markers',
            text=ALL_annotations,
        )

        edge_trace2 = go.Scatter(
            x=[], y=[], line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        for x_edge in ALL_x_edges:
            edge_trace2['x'] += x_edge
        for y_edge in ALL_y_edges:
            edge_trace2['y'] += y_edge

        # for i in range(N):
        #     if random.randint(0, 4) != 3:
        #         continue
        #     target_x, target_y = x_vals[i], y_vals[i]
        #     other_pos = random.randint(0, len(document_titles)-1)
        #     other_x, other_y = x_vals[other_pos], y_vals[other_pos]
        #     edge_trace2['x'] += tuple([target_x, other_x, None])
        #     edge_trace2['y'] += tuple([target_y, other_y, None])

        # -------------------------------------------------------------

        fig = go.Figure(data=[node_trace2, edge_trace2],
                        layout=go.Layout(
                            title='<br>Commodity-documents for all Sections',
                            titlefont=dict(size=16),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            # annotations=[dict(
                            #     text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                            #     showarrow=False,
                            #     xref="paper", yref="paper",
                            #     x=0.005, y=-0.002)],

                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        py.sign_in('digiology', 'e3gE4VleW96Al4evaMEq')
        py.plot(fig, filename='networkx')