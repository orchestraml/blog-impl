from typing import Literal
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


class DataCode(Code):
    """
    Code that takes 1+ Features and returns 1+ Features

    Python:

    """

    input_records_needed = Literal["SingleRecord", "Aggregation", "AllRecords", "Join"]
    """
    (default) SingleRecord: Only requires the data from a single record to execute (e.g., the current record being processed)

    Aggregation: Requires multiple records of data from the same GROUP BY features.

    Join: Requires records obtained by joining to a Dataset with differnet Key(s)

    AllRecords: Requires every record (or a statistical sample if using big data estimation algorithms)

    """

    type = Literal["SQL", "SparkSQL", "pySpark", "Python"]
    """
    What type of code does this block contain?"""


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
