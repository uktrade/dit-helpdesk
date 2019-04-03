import sys
import os
import pandas
import requests
from bs4 import BeautifulSoup

# extract page title based on the url
def extractText(url):
    page = requests.get(url)
    DOM = BeautifulSoup(page.text, 'html.parser')
    text = DOM.head.title.contents[0]
    return text

# read csv helper function
def data_loader(file_path):
    with open(file_path) as f:
        data_frame = pandas.read_csv(f)
    return data_frame

#write csv helper function
def data_writer(source, filename):
    data_frame = pandas.DataFrame(source, columns=['url', 'text'])
    return data_frame.to_csv(filename,index=False)

currentDir = sys.path[0]
sourceFile = 'product_specific_regulations.csv'

# this will just read the first entry for demo
url = data_loader(os.path.join(currentDir,'../../data', sourceFile))['UK Reg'][0]
text = extractText(url)

data_writer({'url': [url], 'text': [text]}, os.path.join(currentDir,'../../data', 'urls_with_text_description.csv'))
