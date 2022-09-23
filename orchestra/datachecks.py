from typing import Optional, Set
from common import Tag


class DataCheck:
    """

    Placeholder for Deequ, PyTest, great_expectation based checks
    """

    tags: Set[Tag]
    """
    Human or machine defined tags for easy indexing and reference
    """

    # TODO: Flesh out data checks.
    # [1] Do we actually need these on ml_transformations?  If so, how do we provide checks for each individual ml_transformation since they are discrete?
    # [2] What libraries do we support and in what order?  deequ, great_expectaions, pytest
    # [3] Where do these get run?  How can we push this to the customer's data infra?


class DataChecksForFeature:
    raw_input_features: Optional[DataCheck]
    raw_input_lookups: Optional[DataCheck]
    post_business_logic: Optional[DataCheck]
    post_ml_transformation: Optional[DataCheck]
