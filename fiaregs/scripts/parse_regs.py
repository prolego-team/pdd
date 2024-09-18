from pathlib import Path
import re

import yaml

from fiaregs.pdfreader import pdf_to_doc
from fiaregs.search.utils.data_utils import Document
import fiaregs.search.utils.doctree as doctree


DOC_DIR = Path('data/docs')
DATA_DIR = Path('data')


# --- PATTERNS AND UTILITIES --

SECTION_HEADINGS_R = (
    (1, r'^(?:ARTICLE\s+)?(\d+[\.\)]?\s)'),
    (1, r'(APPENDIX \d+)'),
    (2, r'^(?:ARTICLE\s+)?(\d+\.\d+\s)'),
    (2, r'^([a-z]\)\s)'),
    (3, r'^(\d+\.\d+\.\d+)'),
    (4, r'^(\(?[ivx]+\))'),  # TODO: this will get confused with (i), (v), (x)
    (5, r'^(\([A-Z]\))')
)

# Utility functions
clean = lambda text: text.replace('\n', ' ').strip()
is_footer = (
    lambda text:
    ('© 2023 Fédération Internationale de l’Automobile' in text) or
    ('2023 Formula 1 Sporting Regulations' in text) or
    (('Page' in text) and ('de' in text))
)
is_header = lambda text: ('ANNEXE L' in text) or ('APPENDIX L' in text)
# clean_section_number = lambda s: s[:-1] if s[-1]=='.' else s

def get_section_label(text: str, section_patterns: tuple) -> tuple[int,str] | None:
    """Take a string and check if it starts with a section label.

    Section labels are assumed to have to up to three parts, each
    part a digit."""
    for level,pattern in section_patterns:
        m = re.match(pattern, text)
        if m is not None:
            return level,m[1]

    return None


def doc_to_blocks(
        doc: Document,
        start_page: int,
        end_page: int,
        section_patterns: tuple
    ) -> list[tuple[int,str]]:
    # Get raw docs
    # Check for section headings and insert paragraph breaks

    # Get clean blocks within the page range
    blocks = [
        (page,block)
        for page in range(start_page, end_page+1)
        for block in doc[page].text_blocks
    ]

    # for block in blocks[:10]:
    #     print(block)
    #     print()

    # Make sure section headings are in their own paragraph
    blocks_new = []
    for page,block in blocks:
        block_new = []
        for line in block.split('\n'):
            sec_label = get_section_label(line, section_patterns)
            if sec_label is not None:
                level, label = sec_label
                if level==1 and line.replace(label,'').isupper():
                    # Start a new block if this is a section heading
                    if len(block_new)>0:
                        blocks_new.append([page, '\n'.join(block_new)])
                    blocks_new.append([page, line])
                    block_new = []
                    continue

            block_new.append(line)

        if len(block_new)>0:
            blocks_new.append([page, '\n'.join(block_new)])

    blocks = blocks_new

    # Clean texts
    blocks = [
        (page,clean(block)) for page,block in blocks
    ]

    # Remove footers
    blocks = [
        [page,block] for page,block in blocks if (not is_footer(block)) and (not is_header(block))
    ]

    # Merge sentences that broke across page breaks
    for i in range(len(blocks[:-1])):
        if blocks[i][0]<blocks[i+1][0]:
            text = blocks[i][1].strip()
            if (len(text)>0) and (text[-1] not in '.!?'):
                blocks[i][1] = blocks[i][1] + ' ' + blocks[i+1][1]
                blocks[i+1][1] = ''
    blocks = [
        (page,block) for page,block in blocks if len(block)>0
    ]

    return blocks


def blocks_to_sections(
        blocks: list[tuple[int,str]],
        filename: str,
        section_patterns: tuple
    ) -> tuple[list[doctree.Section], list[int]]:

    section_levels = [1,]
    sections = [doctree.Section('PREAMBLE', [])]
    prev_secion_label = ''
    for page,paragraph in blocks:
        section_level_label = get_section_label(paragraph, section_patterns)
        if section_level_label is not None:
            level, section_label = section_level_label
            if level==1:
                sections.append(
                    doctree.Section(paragraph, [], {'file':filename, 'page':page})
                )
                section_levels.append(level)
            else:
                if section_label=='(i)' and prev_secion_label!='(h)':
                    level += 1
                elif section_label=='(v)' and prev_secion_label!='(u)':
                    level += 1
                elif section_label=='(x)' and prev_secion_label!='(w)':
                    level += 1
                if section_label=='(ii)' and prev_secion_label=='(i)':
                    section_levels[-1] = level
                elif section_label=='(vi)' and prev_secion_label=='(v)':
                    section_levels[-1] = level
                elif section_label=='(xi)' and prev_secion_label=='(x)':
                    section_levels[-1] = level
                prev_secion_label = section_label
                paragraph_text = paragraph.replace(section_label, '').strip()
                sections.append(
                    doctree.Section(section_label, [paragraph_text], {'file':filename, 'page':page})
                )
                section_levels.append(level)
        else:
            sections[-1].contents.append(paragraph)

    return sections, section_levels

def parse_manual(
        filename: str,
        start_page: int,
        end_page: int | None,
        section_patterns: tuple,
        right_col_only: bool
    ):

    print('Extracting text from PDF...')
    doc = pdf_to_doc(DOC_DIR/filename, right_col_only)
    if end_page is None:
        end_page = len(doc)-1

    print('Converting raw text to clean paragraphs...')
    blocks_clean = doc_to_blocks(doc, start_page, end_page, section_patterns)

    print('Converting paragraphs to hierarchical sections...')
    sections, section_levels = blocks_to_sections(blocks_clean, filename, section_patterns)

    # for section in sections:
    #     print('*'*40)
    #     for paragraph in section.contents:
    #         print('--------')
    #         print(paragraph)

    doc_tree = doctree.parse(sections, section_levels)

    return doc_tree


if __name__=='__main__':
    regs = [
        {
            'filename': 'fia_formula_1_financial_regulations_-_issue_16_-_2023-08-31.pdf',
            'start_page': 1,
            'end_page': 28,
            'right_col_only': False,
            'section_patterns': (
                (1, r'^(\d+[\.\)]?\s)'),
                (1, r'(APPENDIX \d+)'),
                (2, r'^(\d+\.\d+\s)'),
                (3, r'^(\([a-z]\))'),
                (4, r'^(\([ivx]+\))'),  # TODO: this will get confused with (i), (v), (x)
                (5, r'^(\([A-Z]\))')
            ),
            'definitions':
            {
                'start_page':29,
                'end_page':49,
                'right_col_only': False,
                'section_patterns': (
                    (1, r'^(".+")'),
                )
            }
        },
        {
            'filename': 'fia_2023_formula_1_sporting_regulations_-_issue_6_-_2023-08-31.pdf',
            'start_page': 1,
            'end_page': 70,
            'right_col_only': False,
            'section_patterns': (
                (1, r'^(\d+\)\s)'),
                (1, r'(APPENDIX \d+)'),
                (2, r'^(\d+\.\d+\s)'),
                (3, r'^([a-z]\))'),
                (4, r'^([ivx]+\))'),  # TODO: this will get confused with (i), (v), (x)
                (5, r'^([a-z]\))'),   # unreachable
            )
        },
        {
            'filename': '2023_international_sporting_code_fr-en_clean_9.01.2023.pdf',
            'start_page': 1,
            'end_page': 76,
            'right_col_only': True,
            'section_patterns': (
                (1, r'^(?:ARTICLE\s+)(\d+\s)'),
                (1, r'(APPENDIX \d+)'),
                (2, r'^(?:ARTICLE\s+)(\d+\.\d+\s)'),
                (3, r'^(\d+\.\d+\.\d+)\s'),
                (4, r'^(\d+\.\d+\.\d+\.[a-z])'),
            ),
            'definitions': {
                'start_page':77,
                'end_page':85,
                'right_col_only': True,
                'section_patterns': (
                    (1, r'^(.*:)'),
                )
            }
        },
        {
            'filename': 'appendix_l_iv_2023_publie_le_20_juin_2023.pdf',
            'start_page': 0,
            'end_page': None,
            'right_col_only': True,
            'section_patterns': (
                (1, r'^(\d+\.\s)'),
                (2, r'^([a-z]\)\s)'),
                (3, r'^(\d+\.\d+\.\d+)'),
            )
        },
        {
            'filename': 'appendix_l_iii_2023_publie_le_20_juin_2023.pdf',
            'start_page': 0,
            'end_page': None,
            'right_col_only': True,
            'section_patterns': (
                (1, r'^(\d+\.\s)'),
                (2, r'^(\d+\.\d+)\s'),
                (3, r'^([a-z]\)\s)'),
                (4, r'^([ivx]+\))'),
            )
        },
        {
            'filename': 'fia_2023_formula_1_technical_regulations_-_issue_7_-_2023-08-31.pdf',
            'start_page': 5,
            'end_page': 135,
            'right_col_only': False,
            'section_patterns': (
                (1, r'^(?:ARTICLE\s+)(\d+):'),
                (2, r'^(\d+\.\d+\s)'),
                (3, r'^(\d+\.\d+\.\d+)\s'),
                (4, r'^([a-z]\.)\s'),
            ),
            # 'definitions': {
            #     'start_page':77,
            #     'end_page':85,
            #     'right_col_only': True,
            #     'section_patterns': (
            #         (1, r'^(.*:)'),
            #     )
            # }
        },
    ]

    for reg in [regs[-1],]: #regs:
        definitions = reg.pop('definitions', None)
        doc_tree = parse_manual(**reg)
        doc_tree = doctree.consolidate_leaves(doc_tree, 200)
        doc_tree = doctree.consolidate_paragraphs(doc_tree, 100)
        print(doctree.show_tree(doc_tree))

        filename_out = DOC_DIR / reg['filename'].replace('pdf', 'yaml')
        doctree.write(filename_out, doc_tree)

        if definitions:
            definitions['filename'] = reg['filename']
            definition_tree = parse_manual(**definitions)
            print(doctree.show_tree(definition_tree))
            print()
            print(definition_tree[4])
            definition_list = [
                section.title + ' '.join(section.contents)
                for section in definition_tree
            ]
            print(definition_list)

            with open(DOC_DIR / definitions['filename'].replace('pdf', 'defs'), 'w') as f:
                yaml.dump(definition_list, f)
