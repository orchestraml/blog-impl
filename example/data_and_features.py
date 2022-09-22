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

from orchestra.transformers import HuggingFace

# , datetime, pandas as pd

namespace = "cc-fraud"

orchestra = OrchestraClient(
    api_key="74738ff5-5367-5958-9aee-98fffdcd1876",
    organization="my organization",
    namespace="cc-fraud",
)

#####################
# Entities - what "real world things" do we have data about?  are making predictions about?
#####################
# TODO: Should we allow for multiple keys?

user_id = Entity(
    name="user_id",
    type=String,
    tags={"key": "value"},
    description="user_id is globally unique - for de-duplicated accounts, use user_id_dedupped",
    vector_representation="",  # placeholder for embedding-based representation
)

txn_id = Entity(
    name="txn_id",
    type=String,
    description="txn_id identifies every unique credit card transaction - purchases, returns, chargebacks, etc",
    vector_representation="",  # placeholder for embedding-based representation
)


#####################
# Data Sources - what raw data is available about each entity?
# *raw = data made available by other teams, could be either 'gold' tables or 'bronze' tables (using the delta lake parlance)
# we chose to make these schema'd
#####################

user_info = DataSource(  # TODO: better name here - maybe this is ML input data?
    name="users",
    keys=[user_id],
    timestamp_column=Timestamp(
        name="last_updated", type=String, format="yyyyMMdd|hh:ss"
    ),
    output_features=[
        Feature(name="user_address", type=String),
        Feature(name="birthday", type=Date),
    ],
    data_checks="",  # placeholder for data quality and distribution checks
)

txn_log = DataSource(
    name="transactions",
    keys=[txn_id, user_id],
    timestamp_column=Timestamp(name="event_time", type=String, format="yyyyMMdd|hh:ss"),
    output_features=[  # this order has meaning for de-serializing from stream, TODO: how could we be more explicit?
        Feature(
            name="business_name", type=String
        ),  # TODO: do we need a way to differentiate between Feature & RawFeature?
        Feature(
            name="business_address", type=String
        ),  # TODO: do we need a way to differentiate between Feature & RawFeature?
        Feature(name="payment_method", type=String),
        Feature(name="txn_type", type=String),
        Feature(name="purchase_amount", type=Float64),
        Feature(
            name="is_card_present",
            type=Boolean,
            description="Was the transaction conducted with card-not-present (false) or card-present (true)?",
        ),
    ],
    data_checks="",  # placeholder for data quality and distribution checks
)

fraud_labels = DataSource(
    name="fraud_labels",
    keys=[txn_id, user_id],
    timestamp_column=Timestamp(name="timestamp", type=String, format="yyyyMMdd|hh:ss"),
    output_features=[
        Label(name="is_fraud", type=Int32, description="1 is fraud, 0 is not")
    ],
    # type = # indicate this is a source of labels - do we need this?
    data_checks="",  # placeholder for data quality and distribution checks
)

#####################
# Data Providers - what actual places is this raw data coming from?
# There must be at least 1 DataProvider per DataSource per environment
# There can be multiple DataProviders for a DataSource if they are configured to have different latencies
#####################

local_test_sample_training_examples = DataProvider(
    name="fraud-balanced-positive-negative-12022001-10_per_sample",
    owner="eric@orchestraml.com",
    type=DataProvider.types.S3,
    environments=["staging"],
    config={
        "path": "s3://orchestra-ml-prototype-train/creditcardfraud/cc-examples.csv"
    },
)

all_training_examples = DataProvider(
    name="fraud-balanced-positive-negative-12022001",
    owner="eric@orchestraml.com",
    type=DataProvider.types.DBT,
    environments=["production"],
    code={"git": "git://repo/with/dbt-model"},
    config={"command": "dbt run", "final_table": "table_name"},
)

google_sheet = DataProvider(
    name="fraud-manually-labeled-examples",
    type=DataProvider.types.GoogleSheet,
    environments=["development"],
    config={"sheet_name": "Sheet1"},
)

fraud_labels.AddDataProvider(local_test_sample_training_examples)
fraud_labels.AddDataProvider(all_training_examples)
fraud_labels.AddDataProvider(google_sheet)


txn_batch_log = DataProvider(
    name="txn-log-batch",
    type=DataProvider.types.BigQuery,
    environments=["staging", "production"],
    freshness=timedelta(
        hours=8
    ),  # defined to indicate how frequently this table is updated
    config={  # TODO: Make this real, this is just psdeuo-code
        "project": "project-name",
        "instance": "instance-name",
        "table": "fraud_history",
    },
)

# txn_batch_log_sample = DataProvider(
#     name = 'txn-batch-log',
#     type = DataProvider.macros.SampleRows, #built-in type that samples
#     environments = ['development'],
#     config = {
#         'source_data_provider': txn_batch_log,
#         'output_format': 'csv',
#         'sample_percent': 10,
#         'sample_max_rows': 500000,
#         'storage': './'
#     }
# )

txn_stream = DataProvider(
    name="txn-log-stream",
    type=DataProvider.types.Kafka,
    config={  # TODO: Make this real, this is just psdeuo-code
        "bootstrap-url": "some-url"
    },
    environments=["production"],
    freshness=timedelta(milliseconds=50),
)

txn_log.AddDataProvider(txn_stream)
txn_log.AddDataProvider(txn_batch_log)


# TODO: how to define that a "DataSource" can have multiple production sources?  this might make this relationship fall apart
# or maybe we also have to define the features it providers -- answer - 1:1 mapping between Provider & Source.

user_table = DataProvider(
    name="user-demos",
    type=DataProvider.types.BigQuery,
    environments=["development", "staging", "production"],
    freshness=timedelta(hours=8),
    config={  # TODO: Make this real, this is just psdeuo-code
        "project": "project-name",
        "instance": "instance-name",
        "table": "user_table",
    },
)

user_info_api = DataProvider(
    name="user-demo-api",
    type=DataProvider.types.API,
    environments=["staging", "production"],
    freshness=timedelta(seconds=10),
    config={  # TODO: Make this real, this is just psdeuo-code
        "get": "https://some.rest.api/get/users/id:{{user_id}}",
        "credentials": "secret-manager-cred",
    },
)

user_info.AddDataProvider(user_table)
user_info.AddDataProvider(user_info_api)


#####################
# Features - definitions of the inputs that will be used by the model
#####################


hour = Feature(
    # data_sources = [txn_log],
    input_features=["txn_log.timestamp"],
    name="hour",  # Optional, if not provided, function name is used
    type=Int64,
    freshness=timedelta(seconds=45),
    latency=timedelta(seconds=1),
)


# you can define a single feature
@Feature(
    input_features=["txn_log.timestamp"],
    name="hour",  # TODO: should this be output_feature_name? or feature_name?
    type=Int64,
    python_packages={"DateTime": "0.4.7"},
)
def hour(timestamp):
    from datetime import datetime

    return datetime.datetime.fromtimestamp(timestamp).hour


# you can define multiple features
@Features(
    input_features=["txn_log.timestamp"],
    names=[
        "minute",
        "month",
        "day",
        "dayoftheweek",
    ],  # TODO: should this be output_feature_names? or output_features?
    type=Int64,
    python_packages={"DateTime": "0.4.7"},
)
def hour(timestamp):
    from datetime import datetime

    minute = datetime.datetime.fromtimestamp(timestamp).minute
    month = datetime.datetime.fromtimestamp(timestamp).month
    day = datetime.datetime.fromtimestamp(timestamp).day
    dayoftheweek = datetime.datetime.fromtimestamp(timestamp).isoweekday()

    return {  # return a dict
        "minute": minute,
        "month": month,
        "day": day,
        "dayoftheweek": dayoftheweek,
    }


# every value returned by a feature is model-ready (numeric)
# you can accept our default pre-processing
# or you can apply your own

# some features are used directly from the source with Orchestra handling any required pre-processing to get Model ready data.
is_online = Feature(
    input_features=["txn_log.is_card_present"],
    name="is_card_present",
    human_datatype=Boolean,
    business_logic="",
    model_datatype=PreProcess.Auto,  # TODO: better name for this :-)
)

# use our wrapper around common pre-processing libraries
# Orchestra handles the complexity of any .fit() that is required including saving the resulting artifacts
is_online = Feature(
    input_features=["txn_log.is_card_present"],
    name="is_card_present",
    human_datatype=Boolean,
    model_datatype=PreProcess.SciKit.OneHotEncoder,  # TODO: better way to represent this?
)


# this will return [0,1] as a single field to the model

# some features need some pre-processing
txn_type = Feature(
    input_features=["txn_log.txn_type"],
    name="txn_type",
    type=String,
    missing_values={
        "strategy": "default_value",
        "default_value": "point_of_sale",  # TODO: better way to define this?
    },
    transformations={
        "onehot": PreProcess.OneHotEncoder
    }  # these will be automatically applied by orchestra to the values (after all processing such as missing values, code) but before being returned
    # each one creates an additional feature `{original_name}_{key}` with the type set by the function used
    # Feature(name='txn_type_onehot, type= Int32, input_features=['{namespace}.txn_type'], transformations='PreProcess.OneHotEncoder') is returned
)

# the one hot will pass the right values to the model - e.g., all N fields with [0, 1] as needed
# this is great because the level of definition for the feature is understandable by the human (DS + Business user), but also understandable by the model
# this makes for MUCH cleaner code
# and ultimately unlocks ML for less ML savvy people

# pre-trained embeddings are a great way to represent features
# more abstractly, we may use other models to create features

# we will come back to how this model is created later
# but for now, let's assume it was a bert model uptrained by the DS
sentence_bert = Model(
    name="business-description-transformer-model",
    input_features=[Feature(name="business_description", type=String)],
    output_features=[
        Prediction(name="business_description_embedded", type=Float64Vector(128))
        # ^ sub-class of Feature
    ],
)


@Feature(
    input_features=["txn_log.business_name", "txn_log.business_address"],
    name="business_description",
    type=String,
    transformations={
        "bert": sentence_bert
    }  # applied after `business_name + " " + business_address`
    # this is applied by calling the model (hosted on customer infra) for each row
    # saved to Prediction(name='bert', type=Float64Vector(128), input_features=['namespace.business_description'], )
)
def business_description(business_name, business_address):
    return business_name + " " + business_address


# we may also want to define aggregations over multiple rows
# https://feathr.readthedocs.io/en/latest/index.html?highlight=WindowAggTransformation#feathr.WindowAggTransformation
purchase_amount = Feature(
    name="purchase_amount",
    input_features=["txn_log.purchase_amount"],
    type=Float64,
    aggregations={
        "avg_last_5n": Aggregation(
            function="AVG", type="LASTN", window=5, group_by=[user_id]
        ),  # average of the last 5
        # ouptuts Feature(name='purchase_amount_avg_last_5n') #TODO: should we do explicit or auto-names here?
        "avg_last_5mins": Aggregation(
            function="AVG", type="TIME", window=timedelta(minutes=5)
        ),  # average of the last 5 minutes
    },
    # TODO: how can/should we include something like scaling here that applies to the feature itself, but not the aggregations?
    # TODO: how to have a better way to explictly return the raw feature itself here too - its kinda confusing that you get this just by typing name='xx' ...
)


# sometimes we need to look up another value aka joins
@Feature(
    name="transaction_distance_to_user_address",
    input_datasources=[user_info],
    input_features=[
        "txn_log.user_id",
        "txn_log.business_address",
        "txn_log.payment_method",
    ],
    type=Float,
)
# TODO: consider using data_sources pattern for features aka **features, **data_sources
def transaction_distance_to_user_address(
    user_id, business_address, payment_method, **data_sources
):
    """
    Score describing how unexpected the transaction is for the given user.
    """

    def compute_distance_miles(start, end):
        return end - start  # fake code

    if payment_method != "pos":
        return 0.0
    # if the user address and business address are > 150 miles apart and the
    # txn is "pos", flag it with an unexpectedness score of 1.0

    # TODO: what is a more optimal way to define this?
    user_address = data_sources["user_info"].keys([user_id])["user_address"]
    distance = compute_distance_miles(user_address, business_address)
    if distance > 150:
        return 1.0
    else:
        # make unexpectedness proportional to the distance
        return float(distance / 150.0)


# we also need to use features to make other features
unexpectedness_score = Feature(
    name="unexpectedness_score",  # TODO: should this actually be part of the last feature definition?? if not, how do we deal with this naming conflict
    input_features=[
        "{{namespace}}.unexpectedness_score"
    ],  # TODO: does the {{}} work here?
    type=Float64,
    aggregations={
        "avg_last_5n": Aggregation(
            function="AVG", type="LASTN", window=5
        ),  # average of the last 5
    },
    transformations={"scaled": PreProcess.StandardScaler},
)


# sometimes you don't want to think too hard and just embed the string quickly
simple_string = Feature(
    name="free_text_simple_string",
    ######
    transformations={
        "bert": Transformers(
            model="bert-base-uncased", verison="2.0.1"
        )  # Orchestra pre-implements a few of Huggingface models as transformers, this is an open source interface, we just implenent our model class
    },
)
