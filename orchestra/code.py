from typing import Literal, Dict, Optional
from common import Metadata


class Code:
    """
    Parent class of all code types.
    Throws an error if used directly.
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """

    location: str
    """
    TODO placeholder to link to Git"""


class ModelTrainingCode(Code):
    """
    placeholder"""


class DataCode(Code):
    """
    Code that takes 1+ Features and returns 1+ Features

    While some business logic such as `Aggregations` can be declared with Orchestra's library (and thus, the computations automagically orchestrated to run on your data infrastructure), Orchestra gives data scientists the flexibility to define their own custom business logic.  If your business logic fits within the `Aggregations` abstraction, we highly recommend doing so.

    For all other cases, the `DataCode` abstraction contains the business logic used by a `Feature` to transform the `input_features` to the final value.  Accordingly, every `DataCode` object MUST be linked to a `Feature`.

    We strongly suggest you follow the paradigm that data code only operates on the current row of data.  For a subset of DataCode types and freshness latencies, this enables the same code to work across both training and production environments.  However, should you need access to multiple rows of data, Orchestra provides three methods:

    1. If your logic is an aggregation, you can leverage a custom aggregation function [TODO link to custom aggregates]
    2. If your logic requires a join or lookup to another table, you can leverage the `input_datasources` that provides an abstraction to enable Orchestra to deliver the joined or looked-up data to your `DataCode`.
    3. If your logic requires a full table scan, TODO: are there any uses cases for a full table scan outside of ML transformations?

    Adding new types of `DataCode`.  The design of Orchestra is such that we operate blind to the imperative code itself (where orchestration requires awareness, there is a declarative interface) - this makes it straightforward for anyone to add a new data language/provider.

    """

    input_records_needed = Literal["SingleRecord", "Aggregation", "AllRecords", "Join"]
    """
    (default) SingleRecord: Only requires the data from a single record to execute (e.g., the current record being processed)

    Aggregation: Requires multiple records of data from the same GROUP BY features.

    Join: Requires records obtained by joining to a Dataset with differnet Key(s)

    AllRecords: Requires every record (or a statistical sample if using big data estimation algorithms)

    """


class PythonDataCode(DataCode):
    """
    Function definition must be one of these

    def python_data_code(records: List[dict], data_lookups: Dict[str, dict]) -> dict:

        if `input_records_needed` = `Join`, `data_lookups` contains the joined records, otherwise, None
        return value must deliver all `output_features` inside the dict

        if `input_records_needed` = `SingleRecord`, `records` is just 1 record
        Otherwise, all records requested are included.

    def python_data_code(records: pd.Dataframe, data_lookups: Dict[str, pd.Dataframe]) -> pd.Dataframe:

        same as above, just with Dataframes pre-loaded
        return value must deliver all output_features inside the DF

    """

    python_modules: Optional[Dict[str, str]]
    """
    Modules in the form of {'module-nmae', '1.0.33'}
    """

    requirements_txt: str
    """
    requirements.txt file.  Combined with `python_modules` and `conda_yaml`
    """

    conda_yaml: str
    """
    conda.yaml file.  Combined with `python_modules` and `requirements_txt`
    """

    python_version: str
    """
    Python version in the format of '3.7.22'
    """

    docker_container: Optional[str]
    """
    Optional path to a docker container; otherwise the defaults are used
     """


class PySparkDataCode(DataCode):
    """

    def snowpark_data_code(records: pyspark.sql.DataFrame, data_lookups: Dict[str, pyspark.sql.DataFrame]) -> pyspark.sql.DataFrame:

    """


class SparkSQLDataCode(DataCode):
    """ """


class SQLDataCode(DataCode):
    """
    TODO: define this.
    this should be a string return value that can fit in at {XX}

    SELECT
    {XX},
    FROM table [...]

    case when {{input_feature_1}} is 1 then 'no' else 'other' end

    """


class SnowparkDataCode(DataCode):
    """

    Snowpark function

    def snowpark_data_code(records: snowflake.snowpark.DataFrame, data_lookups: Dict[str, snowflake.snowpark.DataFrame]) -> snowflake.snowpark.DataFrame:
    """


# TODO: Where do custom aggregation functions fit in?  I think they should be part of the Aggregations framework, but they will require DataCode...think this through.

# TODO: Define a multiple-feature abstraction e.g., let the data scientist deliver multiple features within one code block.

# TODO: Can we enable Connor's preferred journey (that I think is common) - the DS just wants to write some quick SQL and get some features to test.  How can we bring that into this framework with minimal overhead.  Loose thinking - [1] provide a translator from SQL to Orchestra object [2] use a multiple-feature object and use {{}} vars inside the sql code so we can have some level of understanding of what happens [3] ...

# TODO: Flesh out the table of languages we support.  What are the limtiations of each?  How can we design this to easily allow any data code for any data infra to work without us needing knowledge of that tool's language (e.g., we enable [insert new data tool] very easily)

# TODO: How do we run data code that does NOT run within the data infra?  e.g., SQL is easy to push to the database, but how do we run the Python code?  Probably looks something like a Docker image + push it to K8s within our controlled customer project?  Or maybe within an Airflow job in the customer's project (but we may run into scaling issues)

# TODO: Flesh out how you can define different data code for different environments e.g., production is in Java and development is in Python.  FWIW, I do not like this design pattern, but I think there will probably be some edge cases where it needs to happen.  Think more about this...

# TODO: Add more examples for add't data types
# [1] python code that takes dataframes as inputs
# [2] PySpark and SparkSQL
# [3] others?
