import json
import pandas
from django.shortcuts import _get_queryset
from commodities.models import Commodity
from hierarchy.models import Section
from regulations.models import Regulation


def get_object_or_none(klass, *args, **kwargs):
  queryset = _get_queryset(klass)
  try:
    return queryset.get(*args, **kwargs)
  except queryset.model.DoesNotExist:
    return None


class RegulationsImporter:

    def __init__(self):
        self.data = []

    def data_loader(self, file_path):
        with open(file_path) as f:
            data_frame = pandas.read_csv(f)
        return data_frame

    def instance_builder(self, regulations, data):

        data = self.rename_key(data, "Section ID", "section_id")
        data = self.rename_key(data, "Commodity code", "commodity_id")

        commodity_code = self.normalise_commodity_code(data)

        commodity = get_object_or_none(Commodity, commodity_code=commodity_code)
        section = get_object_or_none(Section, section_id=data['section_id'])

        print (commodity)
        print(section)

        titles = list(regulations.Title)
        types = list(regulations.Type)
        celexes = list(regulations.CELEX)
        urls = list(regulations['UK Reg'])

        document_titles = [doc.strip() for doc in data["Documents"].split('|')]

        documents = [(types[titles.index(title)], celexes[titles.index(title)], urls[titles.index(title)], title)
                                                    for title in document_titles if title in titles]

        for document in documents:
            regulation = Regulation(type=document[0],
                                    celex=document[1],
                                    url=document[2],
                                    title=document[3])
            regulation.save()

            regulation.commodities.add(commodity)
            regulation.sections.add(section)
            regulation.save()


    def normalise_commodity_code(self, data):
        if len(str(data['commodity_id'])) == 9:
            commodity_code = "0{0}".format(data['commodity_id'])
        else:
            commodity_code = str(data['commodity_id'])
        return commodity_code

    def rename_key(self, old_dict, old_name, new_name):
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def load(self, data_path=None):

        if data_path:
            regulations_file = data_path.format('product_specific_regulations.csv')
            commodity_title_file = data_path.format('section_commodity_titles.csv')

            regulations = self.data_loader(regulations_file)
            commodity_titles = json.loads(self.data_loader(commodity_title_file).to_json(orient='records'))

            for item in commodity_titles:
                self.data.append(self.instance_builder(regulations, item))
