#!/usr/bin/python

import sys
import os
from binascii import b2a_hex


###
### pdf-miner requirements
###

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar

def with_pdf (pdf_doc, fn, pdf_pwd, *args):
    """Open the pdf document, and apply the function, returning the results"""
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser)
        # connect the parser and document objects
        parser.set_document(doc)
        # supply the password for initialization
        # doc.initialize(pdf_pwd)

        if doc.is_extractable:
            # apply the function and return the result
            result = fn(doc, *args)

        # close the pdf file
        fp.close()
    except IOError:
        # the file doesn't exist or similar problem
        pass
    return result


###
### Table of Contents
###

def _parse_toc (doc):
    """With an open PDFDocument object, get the table of contents (toc) data
    [this is a higher-order function to be passed to with_pdf()]"""
    toc = []
    try:
        outlines = doc.get_outlines()
        for (level,title,dest,a,se) in outlines:
            toc.append( (level, title) )
    except PDFNoOutlines:
        pass
    return toc

def get_toc (pdf_doc, pdf_pwd=''):
    """Return the table of contents (toc), if any, for this pdf file"""
    return with_pdf(pdf_doc, _parse_toc, pdf_pwd)



###
### Extracting Text
###

def to_bytestring (s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

def update_page_text_hash (h, lt_obj, font_info, leeway = 0.01):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
    # BBOX = left, bottom, right, top
    y0 = lt_obj.bbox[1]
    y1 = lt_obj.bbox[3]
    x0 = lt_obj.bbox[0]
    key_found = False
    for (hash_y0,hash_y1), v in h.items():
        # We want the bottom to be aligned
        if not (y0 >= hash_y1 + leeway or y1 <= hash_y0 - leeway):
        # y0 >= (hash_y0 - leeway) and (hash_y1 + leeway) >= y0 or y1 >= (hash_y0 - leeway) and (hash_y1 + leeway) >= y1 :
            # the text inside this LT* object was positioned at the same
            # width as a prior series of text, so it belongs together
            key_found = True
            v.update({x0 : {
                'text' : to_bytestring(lt_obj.get_text()),
                'font_info' : font_info}})
            h.pop((hash_y0,hash_y1))
            h[(min([hash_y0, y0]),max([hash_y1,y1]))] = v
            break
    if not key_found:
        # New row
        h[(y0,y1)] = {x0 : {
            'text' : to_bytestring(lt_obj.get_text()),
            'font_info' : font_info}}

    return h

def parse_lt_objs (lt_objs, page_number, images_folder, text_content=None):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    if text_content is None:
        text_content = []

    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        # We only care about text
        # text, so arrange is logically based on its column width
        if isinstance(lt_obj, LTTextBox):
            font_info = {'size' : lt_obj._objs[0]._objs[0].size,
                         'font' : lt_obj._objs[0]._objs[0].fontname}
            page_text = update_page_text_hash(page_text, lt_obj, font_info)
        if isinstance(lt_obj, LTTextLine):
            font_info = {'size' : lt_obj._objs[0].size,
                         'font' : lt_obj._objs[0].fontname}
            page_text = update_page_text_hash(page_text, lt_obj, font_info)
    for k, v in sorted(page_text.items(), reverse = True):
        # Seperate columns with --columnbreak--
        ordered_entries = [val for key, val in sorted(v.items())]
        text = [entry['text'].strip('\n').replace('\n',' ') for entry in ordered_entries]
        text_content.append({'text' : text,
                             'font_info' : ordered_entries[0]['font_info']})

    return text_content


###
### Processing Pages
###

def _parse_pages (doc, images_folder, line_margin):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(line_margin = line_margin)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        if i == 25:
            continue
        # if i <= 600:
        #     continue
        print(i)
        
        # if not i == 37:
        #     continue
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may conltain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(parse_lt_objs(layout, (i+1), images_folder))

    return text_content

def get_pages (pdf_doc, line_margin = 0.5, pdf_pwd='', images_folder='/tmp'):
    """Process each of the pages in this pdf file and return a list of strings representing the text found in each page"""
    return with_pdf(pdf_doc, _parse_pages, pdf_pwd, *tuple([images_folder, line_margin]))
