from typing import List, Literal
from datatype import DataType
from code import DataCode
from model import Model
from common import Metadata


class MLTransformation:
    """
    Any transformation logic that translates a human-readable DataTypes into a model-readable DataType
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """

    input_datatype: List[DataType]
    """
    What DataType(s) does this transformation accept?
    """

    output_datatype: List[DataType]
    """
    What DataType(s) does this transformation output?
    """

    input_records_needed = Literal["SingleRecord", "AllRecords"]
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
