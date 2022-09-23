from common import Tag
from typing import Set


class Model:
    """ """

    name: str
    """
    Machine-readable but human-understandable name
    """

    description: str
    """
    Human-readable notes
    """

    tags: Set[Tag]
    """
    Human or machine defined tags for easy indexing and reference
    """
