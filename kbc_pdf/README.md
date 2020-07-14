# KBC PDF Parser

This is a parser based off PDFMiner, which works by splitting pages into lines and then columns. The aim is to parse PDFs like that found at The general steps are:

* Use PDFMiner to extract lines and columns from pages. This stage is based off of the repository found at https://github.com/dpapathanasiou/pdfminer-layout-scanner .
* Find the pages where the tables of interest are. This is done by searching for "Composition of the assets and key figures" in the first line of the page, and then taking all the pages until the phrase "TOTAL NET ASSETS" appears, which marks the end of the table.
* Read the table, line by line, saving the information into a csv file.


## Implementation Notes

Entries in the table with only one column are denoted "side columns". They usually indicate a subtitle for the companies listed below, e.g. the country the companies are in. There is usually a total for each side column at the end, so we can operate it like a stack, pushing new side titles, and popping side titles when the total comes up. This does not necessarily work for countries, where there is no total, so instead we automatically recognise countries from a text file of countries, and then are able to update the country side_title accordingly.
