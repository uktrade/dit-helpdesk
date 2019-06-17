# import pandas as pd
#
# one = pd.read_csv('commodity_category_all_with_synonyms_greenpage.csv')
# two = pd.read_csv('keywords_and_synonyms_merged.csv')

with open('commodity_category_all_with_synonyms_greenpage.csv', 'r') as file1:
    with open('keywords_and_synonyms_merged.csv', 'r') as file2:
        same = set(file1).difference(file2)

same.discard('\n')

with open('some_output_file.txt', 'w') as file_out:
    for line in same:
        file_out.write(line)
