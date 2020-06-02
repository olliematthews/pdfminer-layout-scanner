"""
Analyse a saved pdf
"""


import layout_scanner
from tabula import read_pdf
import pandas as pd
import csv

area = [3.29*72, 0.65*72, 10.69*72, 7.67*72]

pages = layout_scanner.get_pages('../extract-pdfs/pdf_downloads/F00000YJ90.pdf')
dfs = []
table_pages = []
ISIN = 'ISIN'
for page_number, page in enumerate(pages):
    if 'Statement of investments and other net assets' in ''.join(page) and not 'table of contents' in ''.join(page).lower():
        table_pages.append(page)

rows = []
head = ['ISIN', 'Sub-Fund', 'Asset Type', 'Country', 'Description', 'Currency',	'Quantity',	'Market value (note 2)', '% of net assets']

with open('table.csv','w', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(head)

flag = True

for page in table_pages:
    # First we reformat the page into the rows we want
    lines = []
    for l in page:
        l = l.split('--columnbreak')
        
        # Get rid of empty rows
        if all(all(char == ' ' for char in entry) for entry in l):
            continue
        
        # Ignore these lines
        if 'TRANSFERABLE SECURITIES ADMITTED' in l[0]:
            continue
        # Get rid of rows which do not start with text
        try:
            float(l[0].replace(',',''))
            continue
        except:
            pass
                
        # End of table
        if 'The accompanying notes' in l[0]:
            break
        lines.append(l)
        
    split_title = [string.strip(' ') for string in lines[0][0].split('-')]
    fund = split_title[0]
    subfund = '-'.join(split_title[1:])
    description = lines[1][0]
    head = ['ISIN', 'Sub-Fund', 'Asset Type', 'Country']
    head.extend(lines[2])
    
    for line in lines[3:]:
        if len(line) == 3:
            # These are usually 'total' rows. We ignore the results but note there will be a change in asset type after
            if 'TOTAL' in line[0]:
                flag = True
            continue
        
        elif len(line) == 1:
            if flag:
                # flag indicates a change in asset type
                flag = False
                asset_type = line[0].strip(' ')
            else:
                # Else there is a country change
                country = line[0].strip(' ')
            continue
        else:
            # Else, we have a valid row
            if len(line) == 6:
                # This is for bonds, which have two columns at the beginning. We merge these.
                l = [' - '.join(line[:2])]
                l.extend(line[2:])
                line = l
                
            row = [ISIN, subfund, asset_type, country]
            row.extend(line)
            rows.append(row) 

    
with open(fund + '.csv','a', newline = '') as file:
    writer = csv.writer(file)
    for row in rows:
        writer.writerow(row)
        
        