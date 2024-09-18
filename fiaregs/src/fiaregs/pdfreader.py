from typing import Iterable

import fitz
import pdfplumber

from fiaregs.search.utils.data_utils import Page, Document

block_type_to_str = lambda t: 'text' if t==0 else 'image' if t==1 else 'unknown'

def clip(rect: tuple) -> tuple:
    return (rect[2]/2, rect[1], rect[2], rect[3])

def pdf_to_doc(filename: str, right_col_only: bool = False) -> Document:
    crop = lambda rect: clip(rect) if right_col_only else rect
    doc = fitz.open(filename)
    pages_raw = [page.get_text('blocks', clip=crop(page.rect)) for page in doc]
    pages = []
    for i,page in enumerate(pages_raw):
        text_blocks = [
            text
            for xmin,ymin,xmax,ymax,text,block_num,block_type in page
        ]
        pages.append(Page(i, text_blocks))
    doc.close()

    return pages


def pdf_to_doc_plumber(filename: str) -> Document:
    pages = []
    with pdfplumber.open(filename) as pdf:
        for i,page in enumerate(pdf.pages):
            text = page.extract_text(layout=True)

            # Get rid of extra leading/training white space on each line
            text_parsed = '\n'.join([t.strip() for t in text.split('\n')])
            paragraphs = text_parsed.split('\n\n')
            paragraphs = [
                p for p in text_parsed.split('\n\n')
                if len(p)>0]

            pages.append(Page(i, paragraphs))

    return pages



