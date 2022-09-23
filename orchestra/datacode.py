from typing import Literal, Set, Optional
from common import Tag, Metadata


class Code:
    """
    Parent class of all code types.
    Throws an error if used directly.
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """


class DataCode(Code):
    """
    Code that takes 1+ Features and returns 1+ Features

    """

    input_records_needed = Literal["SingleRecord", "Aggregation", "AllRecords", "Join"]
    """
    (default) SingleRecord: Only requires the data from a single record to execute (e.g., the current record being processed)

    Aggregation: Requires multiple records of data from the same GROUP BY features.

    Join: Requires records obtained by joining to a Dataset with differnet Key(s)

    AllRecords: Requires every record (or a statistical sample if using big data estimation algorithms)

    """
