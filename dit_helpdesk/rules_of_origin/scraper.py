from lxml import html
import requests

page = requests.get('https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32013D0094&from=EN')
tree = html.fromstring(page.content)

table_div = tree.xpath('//div[@id="L_2013054EN.01003001"]/')

print(table_div)
