import json
import sys
from pprint import pprint


class Prepper:
    def __init__(self, filepath):
        self.filepath = filepath
        self.input = {}
        self.output = {}

    def data_loader(self):
        with open(self.filepath) as f:
            data = json.load(f)
        self.input = data

    def data_writer(self, file_path, data):
        outfile = open(file_path, "w+")
        json.dump(data, outfile)

    def listify_row_items(self, row):
        obj = {}
        for key, value in row.items():
            if key == "processing_rule":
                obj["workingLeft"] = [value]
            else:
                obj[key] = [value]
        obj["workingRight"] = []
        return obj

    def process_chapter_rows(self, chapter):
        chapter["rows"] = [self.listify_row_items(row) for row in chapter["rows"]]

        rows = []
        for index, row in enumerate(chapter["rows"]):

            print()
            print(row, row["id"] != [""])
            if row["id"] != [""]:
                rows.append(row)

            elif row["id"] == [""]:
                rows[-1]["description"].extend(row["description"])
                rows[-1]["workingLeft"].extend(row["workingLeft"])

        return rows

    def process(self):
        chapters = []
        for chapter in self.input["chapters"]:
            chapter["rows"] = self.process_chapter_rows(chapter)
            chapters.append(chapter)

        self.output["chapters"] = chapters
        self.output["scheme_sid"] = self.input["scheme_sid"]
        self.output["scheme_description"] = self.input["scheme_description"]


path = "/app/dit_helpdesk/rules_of_origin/data/import/"
# filename = 'Autonomous_Trade_Preferences.json'
# filename = 'EPA_Cariforum.json'
# filename = 'EPA_Market_Access_Regulation.json'
# filename = 'Euro-Mediterranean_Free_Trade_Area.json'
# filename = 'FTA_Canada.json'
# filename = 'FTA_Chile_-_Mexico.json'
# filename = 'FTA_Japan.json'
# filename = 'FTA_Singapore.json'
# filename = 'Generalised_System_of_Preferences.json'
# filename = 'GSP_Plus.json'
# filename = 'Specific_Measures_-_Jordan.json'

# filename = 'EPA_South_African_Development_Community_SADC.json'
# filename = 'EPA_Eastern_and_Southern_Africa.json'
# filename = 'FTA_Central_America.json'
# filename = 'FTA_Colombia,_Ecuador_and_Peru.json'
# filename = 'FTA_Deep_and_Comprehensive_Trade_Agreement.json'
# filename = 'FTA_European_Economic_Area_EEA.json'
# filename = 'FTA_South_Korea.json'
# filename = 'Overseas_Countries_and_Territories.json'
filename = "Pan-Euro-Mediterranean_Convention.json"

input_filepath = "{0}_{1}".format(path, filename)
prepper = Prepper(input_filepath)

prepper.data_loader()

prepper.process()

output_filepath = "{0}{1}".format(path, filename)

prepper.data_writer(output_filepath, prepper.output)
