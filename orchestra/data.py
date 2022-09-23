from __future__ import annotations
from dataclasses import dataclass

from typing import Iterable
from pydantic import BaseModel
from typing import List, Optional, Literal


from datatypes import DataType
from datetime import timedelta
from model import Model


class DataCheck:
    """

    Placeholder for Deequ, PyTest, great_expectation based checks
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


class Code:
    """
    Parent class of all code types.
    Throws an error if used directly.
    """


class DataCode(Code):
    """
    Code that takes 1+ Features and returns 1+ Features

    """

    records_needed = Literal["SingleRecord", "Aggregation", "AllRecords", "Join"]
    """
    (default) SingleRecord: Only requires the data from a single record to execute (e.g., the current record being processed)

    Aggregation: Requires multiple records of data from the same GROUP BY features.

    Join: Requires records obtained by joining to a Dataset with differnet Key(s)

    AllRecords: Requires every record (or a statistical sample if using big data estimation algorithms)

    """


class MLTransformation:
    """
    Any transformation logic that translates a human-readable DataTypes into a model-readable DataType
    """

    input_datatype: List[DataType]
    """
    What DataType(s) does this transformation accept?
    """

    output_datatype: List[DataType]
    """
    What DataType(s) does this transformation output?
    """

    records_needed = Literal["SingleRecord", "AllRecords"]
    """
    (default) SingleRecord: Only requires the data from a single record to execute (e.g., the current record being processed).  Examples include image transformations (resize, etc) or embedding models, token lookups, etc.

    AllRecords: Requires every record (or a statistical sample if using big data estimation algorithms)

    #TODO: Any use cases for joins or aggregation aka GROUP BY?  I don't think so...
    """


class AutomaticTransformation(MLTransformation):
    """
    Orchestra applies its pre-defined logic, based on the following hueristics computed using the data:

    TODO: define these hueristics
    """

    # TODO: Implement logic so that this class returns the correct values for output_datatype


class ModelEncoderTransformation(MLTransformation):
    """
    Applies another ML model to the feature's value, for example, applying an embedding model such as BERT to encode a string.
    """

    model: Model


class CustomTransformation(MLTransformation):
    """
    Custom function that operates at a row or dataset level.
    """

    data_code: DataCode
    """
    the code used to deliver this transformation
    """

    # TODO: Define how Custom pre-processing will work


# [1] How do we pass the full dataset if needed to learn?
# [2] How do we enable storing of the learned parameters or artifacts?
# [3] Where does the code itself execute?  How can we make this happen within the customer's current infra?


class SciKitLearnTransformation(MLTransformation):
    """
    Orchestra implemented wrappers around the SciKit pre-processing library
    """

    # TODO: Implement this...

    # TODO: which other libraries do we support for MLTransformations.SciKitLearn?
    # https://scikit-learn.org/stable/modules/classes.html#module-sklearn.preprocessing
    # https://www.tensorflow.org/guide/keras/preprocessing_layers#keras_preprocessing
    # others?


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

    name: str
    """
    Machine-readable but human-understandable name
    """

    description: str
    """
    Human-readable notes
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


class Prediction(Feature):
    """A data value that was generated by a trained ML model.  Includes both predictions served directly to an end user, but also predictions used as part of an `ml_transformation`."""

    model_used: Model
    """
    Output only. Automatically generated by Orchestra based on the Model that made this prediction.
    What `Model` delivered this prediction?  References a specific version. The Model object includes all metadata & lineage such as training data used, version info, etc
    """

    input_features: List[Feature]
    """
    Output only. Automatically generated by Orchestra based on the Model that made this prediction.
    What are the Model's inputs?
    """

    # TODO: Decide if business_logic and ml_transformations can be defined for a Prediction.  I can see a use case where you might use business_logic to transform the raw prediciton into a user-facing value (e.g., if >.5 confidence, use value, otherwise, ...).  Similarly, I can maybe see a use case for ml_transformation where the prediction goes through some sort of normalization??

    ml_transformations: None
    business_logic: None

    # TODO: Will we be able to represent model predictions with human_datatype as-is?  I think we might need to make changes to account for models such as a multi-class model, saving the predic_proba, etc.  It may be that we create a special datatype for prediction and then use human_datatype to represent the value after all business_logic is applied??


class Label(Feature):
    """A data value that is used to train a semi-supervised or supervised ML model"""

    # TODO: I /think/ Label can be identical, but we may want to exclude ml_transformations?  But need to think about this a bit more...


class RawLabel(Label):
    """
    A label that comes directly from a DataProvider without any manipulation.  If it's wrong it is the upstream provider's fault ;-)
    """


class DerivedLabel(Label):
    """
    A label that has business_logic applied to get the correct value.  For example, removing known bad labels, etc.
    """


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


class InputDataView:
    """ """

    name: str
    """
    Machine-readable but human-understandable name
    """

    description: str
    """
    Human-readable notes
    """

    # # machine-readable but human-understandable common name
    # name = ("data_source_name",)
    # # human-readable notes
    # description = ("this source describes X business thing",)
    # # the unique keys that describe the entity contained within this table
    # keys = ([Key(), Key()],)
    # timestamp = (
    #     Timestamp(name="last_updated", human_datatype=String, format="yyyyMMdd|hh:ss"),
    # )
    # # the features provided; in database terms, the schema
    # # `keys` and `timestamp` can be treated by the user as if they were defined as output_features, but the user does not need to include them here
    # output_features = (
    #     [
    #         Feature(),
    #         Feature(),
    #     ],
    # )
    # # Any data quality or data distribution checks that should be performed before passing this data downstream
    # data_checks = ("",)
