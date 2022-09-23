from common import Tag
from typing import Set, Optional


class Model:
    """ """

    name: str
    """
    Machine-readable but human-understandable name
    """

    description: Optional[str]
    """
    Human-readable notes
    """

    tags: Set[Tag]
    """
    Human or machine defined tags for easy indexing and reference
    """
