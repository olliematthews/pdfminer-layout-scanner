"""
Analyse a saved pdf
"""

import layout_scanner
from tabula import read_pdf
import pandas as pd
import csv
import pickle

# Save file
csv_file = 'save_file.csv'
country_file = 'countries.txt'
countries = []
with open(country_file, 'r') as file:
    for line in file:
        countries.append(line.strip('\n').lower())
        
''' Loading the pdf takes ages, so for ease of use it has been saved in a p file'''
# pages = layout_scanner.get_pages('AR_BF029_EN.pdf', line_margin = 0.3)
# pickle.dump(pages, open('pages_long.p','wb'))
pages = pickle.load(open('pages_long.p','rb'))

table_pages = []


table_page_title = 'Composition of the assets and key figures'
table_end = 'PAGENUMBER'


flag = False
# Find the pages with the tables of interest
for page_number, page in enumerate(pages):
    page_text = ''.join([''.join(line['text']) for line in page])
    page_title = page[0]['text'][0]
    if table_page_title in page_title and not page_number < 5:
        flag = True
    if flag:
        table_pages.append(page)
    if 'TOTAL NET ASSETS' in page_text:
        flag = False

rows = []

for page in table_pages:
    # First we reformat the page into the rows we want
    lines = []
    for l in page:
        text = l['text']
        # Get rid of empty rows
        if all(all(char == ' ' for char in entry) for entry in text):
            continue
                        
        # End of table
        if table_end == 'PAGENUMBER':
            if len(text) == 1:
                try:
                    int(text[0])
                    break
                except:
                    pass
        else:
            # Else, we look for a specific phrase
            if table_end in text[0]:
                break
        lines.append(l)
        
        
    line_number = 0
    
    # Extract the fund name if it is there
    if lines[0]['font_info']['size'] == 20.0:
        line_number = 1
        title_line = lines[line_number]
        title = ''
        while(title_line['font_info']['size'] == 14.0):
            title += ' ' + ''.join(title_line['text'])
            line_number += 1
            title_line = lines[line_number]
        fund_start = title.index('of the assets of') + 17
        fund = title[fund_start:]
        # Skip the table header
        line_number += 1
        side_columns = []
        country_level = False

    
    for line in lines[line_number:]:
        text = [entry.strip(' ') for entry in line['text']]
        if 'TOTAL NET ASSETS' in text:
            break
        
        # This indicates a change in the value of a 'side_column' we assign the relevant one
        if len(text) == 1:
            title_text = text[0].strip(' ')
            if country_level:
                if not title_text.lower() in countries:
                    side_columns.pop()
                    country_level = False
                side_columns[-1] = title_text
            else:
                side_columns.append(title_text)
                if title_text.lower() in countries:
                    country_level = True                
            continue
        elif len(text) < 5:
            side_columns.pop()
            country_level = False
            continue
        
        else:
            
            # Else, we have a valid row
            # On these pdfs, commas represent decimal points, can get rid of full stops
            save_text = [text[0], text[2], text[4]]
            
            row = [fund, side_columns[-2], side_columns[-1]]
            
            row.extend(save_text)
            rows.append(row) 

head = ['Fund', 'Asset Type', 'Country', 'Name', 'Currency','Evaluation']


with open(csv_file,'a', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(head)

    for row in rows:
        writer.writerow(row)
        
    