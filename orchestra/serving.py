from typing import List, Set
from common import Metadata
from model import Model
from feature import Feature


class PredictionEndpoint:
    """
    API endpoint for getting a prediction
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """

    template: str
    """placeholder for the template it came from"""

    models: Set[Model]
    """
    what models does this endpoint serve?
    including multiple models here enables A/B testing or other patterns like Bandits.
    """

    api_features: List[Feature]
    """
    what inputs does the API accept?
    this has to be a subset of the union(input_features, keys) of the model(s)
    """

    # TODO expirements
    # TBD - how do we define this?
