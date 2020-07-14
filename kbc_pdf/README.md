# KBC PDF Parser

This is a parser based off PDFMiner, which works by splitting pages into lines and then columns. The aim is to parse PDFs like that found at https://multimediafiles.kbcgroup.eu/ng/feed/am/funds/AR/AR_BF029_EN.pdf . The general steps are:

* Use PDFMiner to extract lines and columns from pages. This stage is based off of the repository found at https://github.com/dpapathanasiou/pdfminer-layout-scanner .
* Find the pages where the tables of interest are. This is done by searching for "Composition of the assets and key figures" in the first line of the page, and then taking all the pages until the phrase "TOTAL NET ASSETS" appears, which marks the end of the table.
* Read the table, line by line, saving the information into a csv file.


## Implementation Notes

* Entries with only one column are usually ignored, unless they are a country, in which case the country of the company is updated.
* In some table entries, the last column is skipped out. We set it to 0 in these cases.
* There is what looks like a bug in PDFMiner where it can struggle to put two lines together in the same text box even when they are within the distance suggested in the parameters. This can cause problems with long company names. In layout_scanner.py, we explicitly correct for this by putting lines together if the company line runs over.

## TODO

The current implementation is rough. Some improvements could be made:

* At the moment, the location of sets of words within each line is ignored. We could group text boxes into columns as well as lines, which would allow us to spot blank entries in the table. This could be useful for other pdfs.
* Having to explicitly force lines to be together when they are within a certain distance is ugly, and not very generalisable. Either find the bug in the PDFMiner code, or rewrite it at a lower level. 
