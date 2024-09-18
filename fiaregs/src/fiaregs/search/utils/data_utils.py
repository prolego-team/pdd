"""Utility functions for search documents."""

from dataclasses import dataclass
from typing import Iterable, Any
from hashlib import md5
import json
from collections import defaultdict

import fiaregs.search.utils.doctree as doctree
from fiaregs.search.utils import tree


@dataclass
class Page:
    """Store a page of text."""
    page_num: int
    text_blocks: list[str]


Document = Iterable[Page]


@dataclass
class SearchResult:
    """Structure for consistent search results."""
    similarity_score: float
    file: str
    tree_index: tuple
    paragraph_index: int
    chunk_id: int
    text: str
    reranked_score: float = -1000


def clean_text(text: str) -> str:
    """Strip white space and newlines from a string."""
    return text.replace('\n','').strip()


def result_to_string(result: SearchResult, doc_trees: dict[str, doctree.DocTree]) -> str:
    """Format a search result as a string with context."""
    file = result.file
    section_ind = result.tree_index

    section = tree.get_from_tree(doc_trees[file], section_ind)
    text = result.text

    top_ind = section_ind
    section_headings = [section.title,]
    while len(next_up:=tree.move_up(top_ind))>0:
        top_ind = next_up
        section_headings.append(tree.get_from_tree(doc_trees[file], top_ind).title)

    section_headings = section_headings[::-1]
    if len(section_headings)<2:
        section_headings.append('None')

    # get additional context
    text = f'**{text}**'
    super_text = doctree.get_supersection(doc_trees[file], section_ind)
    if super_text is not None:
        text = super_text + '\n\n' + text

    sub_text = doctree.get_subsection(doc_trees[file], section_ind)
    if sub_text is not None:
        text = text + '\n\n' + sub_text

    # uri = DOC_DIR / f'{result.metadata["file"]}'
    # uri = uri.absolute().as_uri() + f'#page={result.metadata["page"]}'

    summary_str = (
        f'{file.title()} Regulation: {", ".join(section_headings)}\n\n'
        f'{text}\n'
    )

    return summary_str


def reciprocal_rank_fusion(
      ranked_lists: list[list[Any]], k: float = 60.0
    ) -> list[Any]:
    """Apply reciprocal rank fusion to a list of lists."""
    scores = defaultdict(float)
    for lyst in ranked_lists:
        for rank,item in enumerate(lyst):
            scores[item] += 1/(k + rank)

    scored_items = sorted(
        [(score,item) for item,score in scores.items()],
        key=lambda x: x[0],
        reverse=True
    )

    return [item for _,item in scored_items]


def get_dict_hash(dictionary):
    """
    Calculates a repeatable hash for a dictionary.

    Args:
      dictionary: The dictionary to hash.

    Returns:
      A hash value for the dictionary.
    """
    d_encode = json.dumps(dictionary).encode()
    hasher = md5()
    hasher.update(d_encode)

    return hasher.hexdigest()
