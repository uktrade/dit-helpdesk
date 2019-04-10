import json
import sys
import os
import pandas
import requests
from bs4 import BeautifulSoup

from django.conf import settings
from numpy import nan


class DocumentsScraper:

    def __init__(self):
        self.sourceFile = 'product_specific_regulations.csv'
        self.output_file = 'urls_with_text_description.json'
        self.documents = {}

    def data_writer(self, file_path, data):
        """
        :param file_path:
        :param data:
        :return:
        """
        outfile = open(file_path, 'w+')
        json.dump(data, outfile)


    def extractText(self, url):
        """
        # extract page title based on the url
        :param url:
        :return:
        """
        page = requests.get(url)
        DOM = BeautifulSoup(page.text, 'html.parser')
        text = DOM.head.title.contents[0]
        return text

    def data_loader(self, file_path):
        """
        # read csv helper function
        :param file_path:
        :return:
        """
        with open(file_path) as f:
            data_frame = pandas.read_csv(f)
        return data_frame

    def load(self):
        """
        # this will just read the first entry for demo
        :return:
        """

        data = self.data_loader(settings.REGULATIONS_DATA_PATH.format(self.sourceFile))
        urls = list(data["UK Reg"])
        for url in urls:
            if url is not nan:
                self.documents[url] = self.extractText(url)

        self.data_writer(settings.REGULATIONS_DATA_PATH.format(self.output_file), self.documents)


rs = DocumentsScraper()

rs.load()