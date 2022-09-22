from datetime import timedelta
from orchestra import (
    Label,
    TrainingExamples,
    Environment,
    DataProvider,
    DataSource,
    Feature,
    Features,
    Entity,
    conda,
    pip,
    SnowflakeSource,
    KafkaSource,
    S3Source,
    DevelopmentSampleSource,
    Timestamp,
    Model,
    Prediction,
    Aggregation,
    PreProcess,
    Transformers,
    MLTransformations,
    DataCode,
    DataCheck,
    RawFeature,
    DerivedFeature,
    Key,
    DataSink,
    RawLabel,
    DerivedLabel,
)

from orchestra.DataTypes import (
    # Human-readable only
    String,
    Boolean,
    Timestamp,
    ImageFile,
    AudioFile,
    # Model-readable only
    FloatVector,
    DoubleVector,
    # Either
    Int64,
    Int32,
    Float,
    Double,
)

#####################
# Feature
#####################

feature = Feature(
    # machine-readable but human-understandable common name
    name="feature_name3",
    # human-readable notes
    description="this feature does X, Y, Z",
    # the data used to create this feature, if multiple data sources are used, they must share the same key space
    input_features=["data_source.feature_name1", "data_source.feature_name2"],
    # optional, used for join-like logic or where a value must be looked up from another table that doesn't share the primary key space.  the key(s) of each `input_lookups['datasource_name']` must be present in `input_features` or an error will be thrown
    # only features specified in ['feature_name'] are returned
    input_lookups=[["datasource_name", ["feature_name"]]],
    # the human-readable data type that is output by `business_logic`
    human_datatype=Boolean,
    # Business logic that translates the input_features into this feature.  3 options:
    # 1. Not present - no business logic is required
    # 2. Single piece of logic - the business logic can be represented in a single function
    # 3. 2+ pieces of logic chained together - if the business logic is best computed with multiple steps or there is an aggregation applied after the initial computation
    # More on DataCode() later
    business_logic=[DataCode(), Aggregation()],
    # 1+ MLTransformations, each that defines its output model_datatype(s). 3 options:
    # 1. MLTransformations.Auto: Orchestra applies its pre-defined logic, developed using hueristics on the data itself
    # 2. MLTransformations.SciKitLearn.OneHotEncoder: Orchestra's managed implementation of commonly used libraries #TODO: which libraries should we support?
    # 3. MLTransformations.Custom: Custom function that can operate at a row or dataset level
    # 4. MLTransformations.Model: Apply another ML model to the feature's value, for example, applying an embedding model such as BERT to encode a string
    ml_transformations=[MLTransformations.Auto],
    # How frequently does a feature’s value need to be updated to reflect the most recently available upstream/source data?
    # Technically, if [now() - time_of_last_computation] >= `freshness`, recompute the value if any of input_features have changed within the time window [now() --> time_of_last_computation]
    freshness=timedelta(seconds=1),
    # Any data quality or data distribution checks that should be performed
    data_checks={
        # checks on the input_features before any business_logic is applied
        "input_features": [DataCheck()],
        # checks after business logic is applied
        "post_business_logic": [DataCheck()],
    },
)

aggregation = Aggregation(
    function="AVG", type="LASTN", window=5, group_by=["data_source.feature_name"]
)

# TODO: Define how Custom pre-processing will work
# [1] How do we pass the full dataset if needed to learn?
# [2] How do we enable storing of the learned parameters or artifacts?
# [3] Where does the code itself execute?  How can we make this happen within the customer's current infra?

# TODO: which libraries do we support for MLTransformations.SciKitLearn?
# https://scikit-learn.org/stable/modules/classes.html#module-sklearn.preprocessing
# https://www.tensorflow.org/guide/keras/preprocessing_layers#keras_preprocessing
# others?

# TODO: Flesh out Aggregations concept
# [1] Decide if Aggregations are a special case of business_logic OR a fully seperate concept. I lean towards making it part of business_logic, but to be discussed!
# [2] Define the set of Aggregations we want to support natively
# [3] Define how to write custom Aggregations

# TODO: Do we need a data type for Array or List?

# TODO: Flesh out data checks.
# [1] Do we actually need these on ml_transformations?  If so, how do we provide checks for each individual ml_transformation since they are discrete?
# [2] What libraries do we support and in what order?  deequ, great_expectaions, pytest
# [3] Where do these get run?  How can we push this to the customer's data infra?

# TODO: It might be confusing that model_datatypes isn't explictly defined but rather is defined for each ml_transformations.  Can we improve this?

#####################
# Feature sub-classes
#####################
derived_feature = DerivedFeature(
    # identical, this is the most commonly used class with Orchestra
)

raw_feature = RawFeature(
    #####
    # Same as in Feature, manually set by the user
    #####
    name="",
    description="",
    data_checks="",
    human_datatype="",
    #####
    # automatically generated by Orchestra based on the DataProvider attached to the DataSource
    #####
    freshness="",
    #####
    # not available
    #####
    ml_transformations="",
    business_logic="",
    input_features="",
)

unique_key = Key(
    #####
    # Same as in Feature, manually set by the user
    #####
    name="",
    description="",
    data_checks="",
    human_datatype="",
    #####
    # not available
    #####
    ml_transformations="",
    business_logic="",
    input_features="",
    freshness="",
)

timestamp = Timestamp(
    #####
    # Same as in Feature, manually set by the user
    #####
    name="",
    description="",
    human_datatype="",
    #####
    # New field
    #####
    # the format of the timestamp e.g., seconds since epoch, YYYYmmddHHss, etc
    timestamp_format="",
    #####
    # not available
    #####
    ml_transformations="",
    business_logic="",
    input_features="",
    freshness="",
    data_checks="",
)

prediction = Prediction(
    #####
    # Same as in Feature, manually set by the user
    #####
    name="",
    description="",
    freshness="",
    #####
    # automatically generated by Orchestra based on the Model that made this prediction
    #####
    # the Model's inputs
    input_features=[],
    # the Model object itself, linked to a specific version in the Model Registry
    model=Model(),
    # the same as the output_features of the Model() object [see TODO below]
    human_datatype="",
    #####
    # TBD - see TODO below
    #####
    ml_transformations="",
    business_logic="",
)

derived_label = DerivedLabel(
    #####
    # Same as in DerivedFeature
    # A label that needs business logic applied to get the value
    #####
)

raw_label = RawLabel(
    #####
    # Same as in RawFeature
    # A label that is useful in its existing form
    #####
)

# TODO: Will we be able to represent model predictions with human_datatype as-is?  I think we might need to make changes to account for models such as a multi-class model, saving the predic_proba, etc.  It may be that we create a special datatype for prediction and then use human_datatype to represent the value after all business_logic is applied??

# TODO: Decide if business_logic and ml_transformations can be defined for a Prediction.  I can see a use case where you might use business_logic to transform the raw prediciton into a user-facing value (e.g., if >.5 confidence, use value, otherwise, ...).  Similarly, I can maybe see a use case for ml_transformation where the prediction goes through some sort of normalization??

# TODO: Think more about how model chaining would work.  Its a bit fuzzy to me right now...

# TODO: I /think/ Label can be identical, but we may want to exclude ml_transformations?  But need to think about this a bit more...

# TODO: It might be a bit confusing that Key, DerivedFeature will not have a model_datatypes property.

# TODO: Should timestamp be a special sub-class or not?


data_source = DataSource(
    # machine-readable but human-understandable common name
    name="data_source_name",
    # human-readable notes
    description="this source describes X business thing",
    # the unique keys that describe the entity contained within this table
    keys=[Key(), Key()],
    timestamp=Timestamp(
        name="last_updated", human_datatype=String, format="yyyyMMdd|hh:ss"
    ),
    # the features provided; in database terms, the schema
    # `keys` and `timestamp` can be treated by the user as if they were defined as output_features, but the user does not need to include them here
    output_features=[
        Feature(),
        Feature(),
    ],
    # Any data quality or data distribution checks that should be performed before passing this data downstream
    data_checks="",
)

data_provider = DataProvider(
    # machine-readable but human-understandable common name
    name="data-provider-name",
    # human-readable notes
    description="this provider has Y things",
    # what type of data provider is this?  Must be a pre-defined value from Orchestra's library, although a user can choose to implement their own DataProvider
    type=DataProvider.types.XXX,
    # what dataSource is this provider for?
    data_source=DataSource(),
    # in which environments is this data available for use?  Use cases:
    # [1] Have seperate dataProviders in development vs. production (e.g,. use a local CSV export of sensitive data that's only available with machine-level credentials, etc)
    # [2] Have multiple production dataProviders e.g., Kafka + Snowflake where one provider is used for second- latency features and the other used for week+ latency features.
    environments=[
        Environment.Development,
        Environment.Staging,
        Environment.Production,
        Environment.Custom("name"),
    ],
    # per DataProvider.type configuration, for example
    # [1] S3 path + credentials
    # [2] BigQuery database URI + credentials
    # [3] DBT model directory + run command
    config={"custom_parameter": "value"},
)

data_sink = DataSink()

# TODO: Is there a better name for DataSource?  I think right now it might be a bit confusing, it could be something like "DataSchema" but that feels like it might be a sub-property of a DataProvider rather than the intended top-level entity...

# TODO: Other feature stores split out entity to a top level object.  Why is this?  I keep thinking it feels redundant but maybe there is an advantage to having shared entities when it comes to collaboration particularly when teams are sharing features about many common entities such as users?

# TODO: Flesh out the idea of environments - how are they used?  how does this factor into the CI/CD process?

# TODO: Do we need a way to run DataCode() on a DataProvider?  or, should this be handled by each provider's config?  An example use case might be changing column names, dropping rows that are >x% null, filtering out known bad rows, etc.  I lean to yes...

# TODO: Add in the concept of a data sink.  How will we save things like prediction logs, cached training data, etc.


#####################
# Data Code
#####################


@DataCode(
    # machine-readable but human-understandable common name
    name="data_source_name",
    # human-readable notes
    description="this source describes X business thing",
    # what type of code snippet is this
    type=DataCode.Python,
    # per DataCode.type configuration
    # for example, in Python, this would include pip library definitions
    config={"custom_parameter": "value"},
)
def python_data_code(row_values: dict, data_lookups: dict) -> dict:
    # any imports must be declared above
    import datetime

    # row_values contains the values from the current row
    row_values["data_source.input_feature_2"]
    # data_lookups contains the joined rows input_datasources
    data_lookups["feature_name"]
    # any python code can be called here
    the_value = data_lookups["feature_name"] + row_values["data_source.input_feature_2"]
    return {"name": the_value}


@DataCode(
    ####...####
    type=DataCode.SQL,
)
def sql_data_code():
    return """
        case when {{input_feature_1}} is 1 then 'no' else 'other' end
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

