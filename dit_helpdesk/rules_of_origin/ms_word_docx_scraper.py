import _sre
import re
import sys
from pathlib import Path
from pprint import pprint

from django.conf import settings
from docx import Document
import json


class DocxScraper:

    def __init__(self):
        self.table_dict = {"chapter": []}
        self.table_heading = None
        self.footnotes = {}
        self.data_path = settings.RULES_OF_ORIGIN_DATA_PATH

    def data_loader(self, file_path):
        """

        :param file_path:
        :return:
        """
        with open(file_path) as f:
            json_data = json.load(f, )
        return json_data

    def load(self, docx_file):
        """

        :param docx_file:
        :return:
        """

        document = Document(self.data_path.format("source/{0}".format(docx_file)))

        self.build_footnotes(document)

        rows = self.get_table_rows(document.tables[0])

        self.process_document_table(rows)

        self.data_writer(self.data_path.format("import/{0}".format(docx_file)))

    def get_table_rows(self, table):
        """

        :param table:
        :return:
        """
        return table.rows

    def process_footnote(self, text):
        """

        :param text:
        :return:
        """
        return re.sub(r'\(([\d]+)\)', "(<a href=\"#\\1\">\\1</a>)", text)

    def create_rule_item(self, cells):
        """

        :param cells:
        :return:
        """
        item = {}
        item_keys = ["id", "desc", "workingLeft", "workingRight"]

        if len(cells) == 4:
            for i in range(len(item_keys)):
                item[item_keys[i]] = cells[i]
        elif len(cells) == 3:
            cells.append('')
            for i in range(len(item_keys)):
                item[item_keys[i]] = cells[i]
        else:
            for i in range(len(item_keys)):
                item[item_keys[i]] = cells[i]
        # pprint(item)
        return item

    def iter_unique_cells(self, row):
        """

        :param row:
        :return:
        """
        """Generate cells in *row* skipping empty grid cells."""
        prior_tc = None
        for cell in row.cells:
            this_tc = cell._tc
            if this_tc is prior_tc:
                continue
            prior_tc = this_tc
            yield cell

    def process_document_table(self, rows):
        """

        :param rows:
        :return:
        """

        for row in rows:

            if self.is_table_heading(row):
                print(self.is_table_heading(row))
                continue
            if self.is_column_number_row(row):
                print(self.is_table_heading(row))
                continue
            row = self.process_row(row)

            if "Chapter" in row[0]:
                chapter_num = re.search(r"Chapter ([\d]+)", row[0])
                item = self.get_chapter_number(chapter_num.group(1))
                item['row'].append(self.create_rule_item(row))
                self.table_dict["chapter"].append(item)

            else:
                last_chapter_idx = len(self.table_dict["chapter"]) - 1
                self.table_dict['chapter'][last_chapter_idx]['row'].append(self.create_rule_item(row))

    def is_table_heading(self, row):
        cells = self.iter_unique_cells(row)
        heading_list = [[para.text for para in cell.paragraphs if para.text != '']
                              for cell in cells]
        heading_list = [cell[0] if len(cell) > 0 else '' for cell in heading_list]
        return "heading" in heading_list[0].lower() or "commodity code" in heading_list[0].lower() and "Description" in heading_list[1]

    def get_chapter_number(self, number):
        return {'number': "{0:02d}".format(int(number)), 'row': []}

    def build_footnotes(self, document):
        """

        :param document:
        :return:
        """

        pattern = r'^\(([\d]+)\)\s(.+)$'
        footnote_matches = [re.match(pattern, paragraph.text) for paragraph in document.paragraphs]

        for footnote in footnote_matches:
            if footnote is not None:
                self.footnotes[footnote.group(1)] = footnote.group(2)

    def data_writer(self, file_path):
        """

        :param file_path:
        :param data:
        :return:
        """
        file_name = Path(file_path).stem.upper()

        outfile = open(self.data_path.format("import/{0}.json".format(file_name)), 'w+')
        json.dump(self.table_dict, outfile)

    def is_column_number_row(self, row):
        """

        :param row:
        :return:
        """

        pattern = "\(([\d]+)\)|(or)"
        cells = self.iter_unique_cells(row)
        row_cells = [[para.text for para in cell.paragraphs if para.text != ''] for cell in cells]
        matches = [re.match(pattern, cell[0]) if len(cell) > 0 else '' for cell in row_cells]
        return None not in matches

    def process_row(self, table_row):
        """

        :param table_row:
        :return:
        """

        cells = self.iter_unique_cells(table_row)
        row_cells = [[para.text for para in cell.paragraphs if para.text != ''] for cell in cells]
        row = [cell[0] if len(cell) > 0 and "\xa0" not in cell[0] else '' for cell in row_cells]
        return row

