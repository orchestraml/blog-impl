from typing import Tuple, Optional, Set


class Tag(Tuple):
    """key: value pair that is user definable.
    Used to store information on any top-level object.
    """

    key: str
    value: str


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

    tags: Set[Tag]
    """
    Human or machine defined tags for easy indexing and reference
    """
