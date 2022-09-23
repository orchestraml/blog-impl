from typing import List, Set, Optional

from feature import Key, Timestamp, Feature
from datacheck import DataCheck
from environment import EnvironmentType
from common import Tag, Metadata


class DataProviderType:
    """
    What is the actual data infra?  BigQuery, Snowflake, S3, Google Sheests, Kafka, etc
    """

    # TODO: implement this


class InputDataSchema:
    """
    `InputDataSchema` defines the schema of data (aka RawFeatures) ingested by data scientists to further manipulate into DerivedFeatures that a Model can process.

    `InputDataProviders` defines an actual data source (e.g., database, s3/blob store bucket, kafka streem, google sheet, etc) that provides data in the schema defined by `InputDataSchema`.

    Together, `InputDataSchema` and `InputDataProviders` are designed to provide a clean abstraction between the upstream data sources (that data scientists have little to no control over, but are extremely dependent upon) and the feature engineering work (that data scientists have complete control over).

    Why separate `InputDataSchema` from the `InputDataProviders`?

    Particularly when building user-facing models, it is common to have training data come from a one data provider (e.g., an analytical warehouse or data lake with historical data) and production data (that is fed to the model for a prediction) come from a combination of data providers (e.g., features requiring a week+ freshness are computed from analytical data sources and cached while features requiring a second- freshness are computed in near real time from a streaming data source).

    Of course, for the model to actually work, these multiple data sources must deliver the same data schema, hence the abstraction that supports a specific definition.

    The `InputDataSchema` abstraction enables Orchestra to intelligently orchestrate your data infrastructure, for example, applying schema over an unstructured Kafka stream or alerting when data quality checks fail on one source.
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """

    keys: List[Key]
    """
    The unique keys that describe the entity contained within this table.  For example, [user_id, transaction_id}.
    Often referred to as:
    * Primary key
    * Data grain
    * Entity
    * ... others ...
    """

    # TODO: Other feature stores split out entity to a top level object.  Why is this?  I keep thinking it feels redundant but maybe there is an advantage to having shared entities when it comes to collaboration particularly when teams are sharing features about many common entities such as users?

    timestamp: Timestamp
    """
    Which column of data has the timestamp of the record?
    Used to support time-travel-aware joins.
    """

    output_features: List[Feature]
    """
    The `Features` delivered by a InputDataProvider confirming to this `InputDataSchema`.
    
    In database terms, the schema.

    `keys` and `timestamp` can be treated by the user as if they were defined as output_features.  Orchestra automatically appends these Features to the list.
    """

    data_checks: List[DataCheck]
    """
    Any data quality or data distribution checks that should be performed on the incoming data.  Executed by Orchesrta using the user's supplied checking framwork.
    """


class DataProviderConfig:
    """
    Configuration settings for a specific provider
    For example
    # [1] S3 path + credentials
    # [2] BigQuery database URI + credentials
    # [3] DBT model directory + run command
    """

    # TODO: implement this to be key:value pairs


class InputDataSource:
    """
    `InputDataSchema` defines the schema of data (aka RawFeatures) ingested by data scientists to further manipulate into DerivedFeatures that a Model can process.

    `InputDataProviders` defines an actual data source (e.g., database, s3/blob store bucket, kafka streem, google sheet, etc) that provides data in the schema defined by `InputDataSchema`.

    Together, `InputDataSchema` and `InputDataProviders` are designed to provide a clean abstraction between the upstream data sources (that data scientists have little to no control over, but are extremely dependent upon) and the feature engineering work (that data scientists have complete control over).

    Why separate `InputDataSchema` from the `InputDataProviders`?

    Particularly when building user-facing models, it is common to have training data come from a one data provider (e.g., an analytical warehouse or data lake with historical data) and production data (that is fed to the model for a prediction) come from a combination of data providers (e.g., features requiring a week+ freshness are computed from analytical data sources and cached while features requiring a second- freshness are computed in near real time from a streaming data source).

    Of course, for the model to actually work, these multiple data sources must deliver the same data schema, hence the abstraction that supports a specific definition.

    The `InputDataSchema` abstraction enables Orchestra to intelligently orchestrate your data infrastructure, for example, applying schema over an unstructured Kafka stream or alerting when data quality checks fail on one source.
    """

    metadata: Metadata
    """
    name, description, key:value tags
    """

    provider: DataProviderType
    """
    What is the actual infra?  BigQuery, Snowflake, S3, Google Sheests, Kafka, etc
    """

    provider_config: DataProviderConfig
    """
    Configuration settings for a specific provider
    For example:
    [1] S3 path + credentials
    [2] BigQuery database URI + credentials
    [3] DBT model directory + run command"""

    environment: Set[EnvironmentType]
    """
    In which environments is this data available for use?  Use cases:
    [1] Have seperate DatasetProviders in development vs. production (e.g,. use a local CSV export of sensitive data that's only available with machine-level credentials, etc)
    [2] Have multiple production DatasetProviders e.g., Kafka + Snowflake where one provider is used for second- latency features and the other used for week+ latency features.
    """

    # TODO: Do we need a way to run DataCode() on a InputDataProvider?  or, should this be handled by each provider's config?  An example use case might be changing column names, dropping rows that are >x% null, filtering out known bad rows, etc.  I lean to yes...


class OutputDataDestination:
    """ """

    # TODO: Add in the concept of a data sink.  How will we save things like prediction logs, cached training data, etc.
