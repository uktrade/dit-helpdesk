import json

import pandas
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from numpy import nan


def extract_html_title(url):
    """
    Helper function to extract the page title based on the url
    :param url: url being requested
    :return: string representing the title
    """
    page = requests.get(url)
    dom = BeautifulSoup(page.text, 'html.parser')
    text = dom.head.title.contents[0]
    return text


def data_writer(file_path, data):
    """
    Helper function to write a python data structure to json file
    :param file_path: the file path to write to
    :param data: the data to write
    """
    outfile = open(file_path, 'w+')
    json.dump(data, outfile)


def data_loader(file_path):
    """
    Helper function to load csv file data into a pandas data frame
    :param file_path: file path to read
    :return: pandas data frame object
    """
    with open(file_path) as f:
        data_frame = pandas.read_csv(f)
    return data_frame


class DocumentScraper:

    def __init__(self):
        self.source_file = 'product_specific_regulations.csv'
        self.output_file = 'urls_with_text_description.json'
        self.documents = {}

    def load(self):
        """
        Method to load csv data from the target sourcefile
        extract the list of urls
        and build a dictionary of document titles keyed on the url
        and write that data to an output file for use by the importer

        :return:
        """

        data = data_loader(settings.REGULATIONS_DATA_PATH.format(self.source_file))
        urls = list(data["UK Reg"])
        for url in urls:
            if url is not nan:
                self.append_url_title(url)

        data_writer(settings.REGULATIONS_DATA_PATH.format(self.output_file), self.documents)

    def append_url_title(self, url):
        self.documents[url] = extract_html_title(url)
