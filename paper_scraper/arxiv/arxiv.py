from datetime import datetime
from typing import List, Union

import arxiv
from paper_scraper.arxiv.utils import get_query_from_keywords
from paper_scraper.utils import dump_papers

arxiv_field_mapper = {
    'published': 'date',
    'journal_reference': 'journal',
    'summary': 'abstract'
}

# Authors and date fields needs specific processing
process_fields = {
    'date': lambda date: datetime.fromisoformat(date[:10]).date(),
    'journal': lambda j: j if j is not None else ''
}


def get_arxiv_papers(
    query: str,
    fields: List = ['title', 'authors', 'date', 'abstract', 'journal', 'doi'],
    *args,
    **kwargs
):
    """
    Performs arxiv API request of a given query and returns list of papers with
    fields as desired.

    Args:
        query (str): Query to arxiv API. Needs to match the arxiv API notation.
        fields (list[str]): List of strings with fields to keep in output.
        *args, **kwargs are additional arguments for arxiv.query

    Returns:
        list of dicts. One dict per paper.

    """
    raw = arxiv.query(query=query, *args, **kwargs)

    processed = [
        {
            arxiv_field_mapper.get(key, key):
            process_fields.get(key, lambda x: x)(value)
            for key, value in paper.items()
            if arxiv_field_mapper.get(key, key) in fields
        } for paper in raw
    ]
    return processed


def get_and_dump_arxiv_papers(
    keywords: List[Union[str, List[str]]],
    filepath: str,
    fields: List = ['title', 'authors', 'date', 'abstract', 'journal', 'doi'],
    *args,
    **kwargs
):
    """
    Combines get_arxiv_papers and dump_papers.

    Args:
        keywords (List[str, List[str]]): List of keywords to request arxiv API.
            The outer list level will be considered as AND separated keys, the
            inner level as OR separated.
        filepath (str): Path where the dump will be saved.
        fields (List, optional): List of strings with fields to keep in output.
            Defaults to ['title', 'authors', 'date', 'abstract',
            'journal', 'doi'].
    """
    # Translate keywords into query.
    query = get_query_from_keywords(keywords)
    papers = get_arxiv_papers(query, fields, *args, **kwargs)
    dump_papers(papers, filepath)
