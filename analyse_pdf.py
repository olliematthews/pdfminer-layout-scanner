"""
Analyse a saved pdf
"""


import layout_scanner
from tabula import read_pdf
import pandas as pd

area = [3.29*72, 0.65*72, 10.69*72, 7.67*72]

pages = layout_scanner.get_pages('../extract-pdfs/pdf_downloads/F00000YJ90.pdf')
dfs = []
table_pages = []
# for page_number, page in enumerate(pages):
#     if 'Statement of investments and other net assets' in page and not 'table of contents' in page.lower():
#         table_pages.append(page)

with open('table.csv', 'w') as file:
    for line in pages[0]:
        file.write(line.replace('--columnbreak--', ',') + '\n')
        