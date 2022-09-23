from typing import Tuple, Optional


class Metadata(Tuple):
    """
    Metadata about the given object
    """

    name: str
    """
    Machine-readable but human-understandable name
    """

    description: Optional[str]
    """
    Human-readable notes
    """

    tags: dict
    """
    Human or machine defined tags for easy indexing and reference
    """
