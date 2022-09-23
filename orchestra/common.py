from typing import Tuple


class Tag(Tuple):
    """key: value pair that is user definable.
    Used to store information on any top-level object.
    """

    key: str
    value: str
