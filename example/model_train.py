from data_and_features import (
    fraud_labels,
    local_test_sample_training_examples,
    hour,
    minute,
    month,
    day,
    dayofweek,
    is_online,
    txn_type,
    business_description,
    purchase_amount,
    transaction_distance_to_user_address,
    unexpectedness_score,
)

from orchestra import OrchestraClient

from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

orchestra = OrchestraClient(
    api_key="74738ff5-5367-5958-9aee-98fffdcd1876",
    organization="my organization",
    namespace="cc-fraud",
)


# the_link is a way to reference this data set
(X_train, X_test, y_train, y_test, the_link) = orchestra.get_training_data(
    training_examples_data_source=fraud_labels,
    training_examples_data_provider=local_test_sample_training_examples,
    features=[
        hour,
        minute,
        month,
        day,
        dayofweek,
        is_online,
        txn_type,
        business_description,
        purchase_amount,
        transaction_distance_to_user_address,
        unexpectedness_score,
    ],
)

if the_link.data_validation is False:
    print("bad data - figure it out")
    # at this point, orchestra would have dumped enough information to figure the problem out
    # plus there would be an interactive UX to help...
    exit

model_name = "cc-fraud-xgb"
start_train = orchestra.log_modeltraining_code(model_name).start(the_link)

# this gets the organization's MLFlow instance
# mlflow is the native Mlflow object - Orchestra just has a silent wrapper on top so we can be a bit smart ;-)
mlflow = orchestra.init_mlflow()

with mlflow.start_run():

    xgb = XGBClassifier(max_depth=4)
    xgb.fit(X_train, y_train)

    xgb_yhat = xgb.predict(X_test)
    ascore = accuracy_score(y_test, xgb_yhat)
    print("Accuracy score of the XGBoost model is {}".format(ascore))

    mlflow.log_metric("accuracy_score", ascore)

    f1score = f1_score(y_test, xgb_yhat)
    print("F1 score of the XGBoost model is {}".format(f1score))

    mlflow.log_metric("f1_score", f1score)

    mlflow.sklearn.log_model(xgb, model_name, registered_model_name=model_name)

    mlflow_uri = mlflow.geturi()  # this is fake code but i know this function exists

    # this registers everything about the model as a Model() object
    # the features, the training data, the splits, etc, etc
    # it also syncs feature info to MLflow as tags
    orchestra.log_model(mlflow_uri, the_link)


start_train.end()


# now, imagine how a feature expirementation tool here would work

# define the expirement

# Register expirement
orchestra.register_expirement(
    name="cc-fraud-new-features",
    new_features=[
        "txn_data.user_age",
        "txn_data.hour",
        "txn_data.average_last5_purchases",
    ],
    expirement_config={
        "algorithm": "try_all_permutations",
        "metrics": ["f1_score"],
        "metrics_goals": ["maximize"],
    },
)

# Get all feature sets for this expirement
features_for_all_expirements = orchestra.get_training_data(
    feature_expirement="cc-fraud-new-features"
)

# Train models for each feature set in the expirement
for feature_set in features_for_all_expirements:
    (X_train, X_test, y_train, y_test) = feature_set.data

    xgb = ""  # //train the model//
    f1score = ""  # //compute the score//

    # SAME CODE AS ABOVE

# now, you compare expirements within MLFlow UI ...

# imagine this same idea, but now for different `ml_transformations`...
