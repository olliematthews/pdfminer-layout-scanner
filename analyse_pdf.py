"""
Analyse a saved pdf
"""


import layout_scanner
from tabula import read_pdf
import pandas as pd
import csv


# Save file
csv_file = 'save_file.csv'
ISIN = 'NA'

pages = layout_scanner.get_pages('orcadia_pdf.pdf')
dfs = []
table_pages = []


table_page_title = 'Statement of investments and other net assets'
toc_title = 'table of contents'
table_end = 'The accompanying notes'
start_row = 3
total_row_len = 3
side_column_titles = ['Asset Type', 'Country']


# Find the pages with the tables of interest
for page_number, page in enumerate(pages):
    if table_page_title in ''.join(page) and not toc_title in ''.join(page).lower():
        table_pages.append(page)

rows = []
head = ['ISIN', 'Sub-Fund', 'Asset Type', 'Country', 'Description', 'Currency',	'Quantity',	'Market value (note 2)', '% of net assets']

with open(csv_file,'w+', newline = '') as file:
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
        if table_end in l[0]:
            break
        lines.append(l)
        
    split_title = [string.strip(' ') for string in lines[0][0].split('-')]
    fund = split_title[0]
    subfund = '-'.join(split_title[1:])
    description = lines[1][0]
    head = ['ISIN', 'Sub-Fund', 'Asset Type', 'Country']
    head.extend(lines[2])
    depth = 0
    side_columns = [0] * len(side_column_titles)
    
    for line in lines[start_row:]:
        if len(line) == total_row_len:
            # These are  'total' rows. We ignore the results but note there will be a change in asset type after
            if 'TOTAL' in line[0]:
                depth -= 1
            continue
        
        # This indicates a change in the value of a 'side_column' we assign the relevant one
        elif len(line) == 1:
            side_columns[depth] = line[0].strip(' ')
            if depth < len(side_columns) - 1:
                depth += 1
            continue
        else:
            # Else, we have a valid row
            if len(line) == 6:
                # This is for bonds, which have two columns at the beginning. We merge these.
                l = [' - '.join(line[:2])]
                l.extend(line[2:])
                line = l
                
            row = [ISIN, subfund, side_columns[0], side_columns[1]]
            row.extend(line)
            rows.append(row) 

    
with open(csv_file,'a', newline = '') as file:
    writer = csv.writer(file)
    for row in rows:
        writer.writerow(row)
        
        