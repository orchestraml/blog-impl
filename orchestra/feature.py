from __future__ import annotations
from dataclasses import dataclass

from typing import List, Optional, Literal


from datatype import DataType
from datetime import timedelta

from common import Metadata
from code import DataCode
from datacheck import DataChecksForFeature


@dataclass
class Feature:
    """An individual feature.

    Visual depiction: https://ibb.co/9t2zhXS

    Features form the basis of machine learning and are the core unit of abstraction in Orchestra's data model.

    Author's note (EP):
    I've heard different perspectives on what a "feature" is, particularly when speaking to practitioners who exclusively work with modern NLP or computer vision techniques and only have model inputs that are embeddings (floating point vectors) created directly from the raw data without any business logic (e.g., text —> embedding or image —> embedding).  In this situation, I often hear "we don't have features, we just use embeddings as model input” although I have also heard "we do a bit of text clean up before applying an embedding based model in order to reduce our cost profile so it is a feature."

    I believe there is great benefit to creating a common definition of a Feature that includes both modern techniques (ala transformers, etc) and traditionally engineered features (ala feature engineering) as I expect for the foreseeable future (note 1) a single company's full breadth of models will include both.  This common definition will also ease communication with business stakeholders about how machine learning works.
    """

    def __init__():
        super().__init__()
        return

    metadata: Metadata
    """
    name, description, key:value tags
    """

    input_features: List[Feature]
    """
    The input data used to create this feature.

    If Features from 2+ different `Datasets` are used, both `Datasets` must share the same `Key` space.
    """

    input_lookups: Optional[List[Feature]]
    """
    Optional, used for join-like logic or where a value must be looked up from another table that doesn't share the primary key space. 
    
    The `Key(s)` of each `input_lookups[Feature]`'s `Dataset` must be included as `input_features`
    """

    human_datatype: DataType
    """
    The human-readable data type that is output by the code specified by `business_logic`
    """

    model_datatypes: List[DataType]
    """
    Output only.  Set automatically based on the `ml_transformations.output_datatype`'s"""

    business_logics: Optional[List[DataCode]]
    """
    Optional. Business logic that translates the input_features into this feature.  Each provided DataCode is executed in order, passing information between steps.

    Can be 1+ DataCodes. 

    A transformation created based on a business understanding of the data in order to provide additional context to the model in order to accelerate or simplify how it learns patterns in the data.  Examples include calculating a total purchase amount that includes tax, collapsing categories that are actually the same, etc.  Business logic is optional (for example, if the feature is “chat message” there is no need for additional business logic).  

    A common piece of business logic to apply is an aggregation over multiple rows of data, or combining values over a specific time period through an average, count, sum, etc (in SQL, this is referred to as a GROUP BY).  This pattern creates complexity for productionizing features since at model inference time, typically only the current row of data is available.  Orchestra's Aggregation abstraction simplifies the process of writing production-ready aggregations [see action items below for a discussion].

    Author's note (EP): In my conversations with 100s of ML practitioners, I have heard inconsistency in what each of these 2 steps (business logic, ML-specific transformations) are called.  Some say “feature engineering”, some say “pre-processing”, some use a combination of both terms.  Potato-patato.  Irregardless of what you call it, folks apply business logic, then transform everything to numbers.
   
    """

    ml_transformations: Optional[List[MLTransformation]]
    """
    Optional ML transformations (aka pre-processing aka functions that translate from human-readable data to model-readable data).
    
    If not provided, Orchestra will check that only model-readable DataTypes pass through.

    ML-specific transformations: a transformation that is done only for the purposes of translating the data into a format a model can understand.  Said differently, these transformations would never happen outside the context of machine learning (e.g., would not be done inside a traditional BI table) and do NOT change what the data describes, only how the data is represented (e.g., a ML transformation will not go from “meaning A” to “meaning B”).

    Author's note (EP): In my conversations with 100s of ML practitioners, I have heard inconsistency in what each of these 2 steps (business logic, ML-specific transformations) are called.  Some say “feature engineering”, some say “pre-processing”, some use a combination of both terms.  Potato-patato.  Irregardless of what you call it, folks apply business logic, then transform everything to numbers.

    """

    freshness: timedelta
    """
    How frequently does this feature's value need to be updated to reflect the most recently available upstream/source data?

    Implemented as: If [now() - time_of_last_computation] >= `freshness`, recompute the value if any of input_features have changed within the time window [now() --> time_of_last_computation]
    
    """

    data_checks: Optional[DataChecksForFeature]
    """
    Any data quality or data distribution checks that should be performed.  Executed by Orchesrta using the user's supplied checking framwork.
    """


class RawFeature(Feature):
    """
    Data that comes directly from a DataProvider and will never be manipulated directly by Orchestra.  If a value here is “bad” - it is 100% the fault of the DataProvider's owner 😉
    """

    ml_transformations: None
    business_logic: None
    input_features: None

    freshness: timedelta
    """
    Output only.
    Automatically generated by Orchestra based on the DatasetProvider attached to the Dataset
    """


class DerivedFeature(Feature):
    """
    Data that is manipulated by Orchestra based on the user's declarations.  This is the most commonly used class within Orchestra.
    """


class Key(Feature):
    """A primary or secondary key field.  Used for aggregations and lookups."""

    ml_transformations: None
    business_logic: None
    input_features: None
    freshness: None
    model_datatypes: None


class Timestamp(Feature):
    """
    A data value that represents the timestamp of when other Features in that row of data were created or updated.  Used for time-travel and time-aware joins.
    """

    timestamp_format: str
    """
    Format of the timestamp e.g., seconds since epoch, YYYYmmddHHss, etc
    """

    # TODO: Should timestamp be a special sub-class or not? I think yes but 85% sure.

    ml_transformations: None
    business_logic: None
    input_features: None
    freshness: None
    data_checks: None


class Aggregation(DataCode):
    """
    Defines an aggregation function.

    aka GROUP BY in SQL

    """

    records_needed: Literal["Aggregation"]
    """
    Default value, can't be changed
    """

    aggregate_function: Literal["SUM", "COUNT", "MAX", "MIN", "AVG", "CUSTOM"]
    """
    What function is used to compute the aggregation?

    All except CUSTOM are built-in to Orchestra.

    SELECT aggregate_function(Feature) FROM ...

    Credit: Portions borrowed from the Feathr spec 
    """

    aggregate_by: List[Feature]
    """
    What Features are we aggregating by?

    ... GROUP BY [aggregate_by, ...]
    """

    custom_function: Optional[DataCode]
    """
        TODO: define the limits of what types of DataCode can be provided here
    """

    window: str
    """
    Either a time window or the last N records.

    d(day)
    h(hour)
    m(minute)
    s(second)
    n(last n records)
    
    Examples: “7d’ or “5h” or “3m” or “1s” or "5n"

    Any time window: ... WHERE now() - record_timestamp <= window
    Any N window: ... ORDER BY [order_by, ...] LIMIT n

    Credit: Portions borrowed from the Feathr spec 
    """

    order_by: Optional[tuple(List[Feature], Literal["DESC", "ASC"])]
    """
    Features to sort the records by

    Only applies if window is a last N records.
    """
