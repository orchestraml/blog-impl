from orchestra import OrchestraClient, GetModel, ModelEndpoint

from model_train import model_name

orchestra = OrchestraClient(
    api_key="74738ff5-5367-5958-9aee-98fffdcd1876",
    organization="my organization",
    namespace="cc-fraud",
)

# TODO: the training job config

# serving config

model = GetModel(name=model_name, version="latest")  # how can we hard link the version?

features = model.features()

model_server = ModelEndpoint(
    # machine-readable but human-understandable common name
    name="cc-fraud-main",
    # human-readable notes
    description="dont fraud me",
    # what models does this endpoint serve?
    # including multiple models here enables A/B testing or other patterns like Bandits.
    models=[model],
    # everything else comes from Orchestra behind the scenes
    api_features=[
        features["user_id"],
        features["txn_id"],
        features["timestamp"],
        features["purchase_amount"],
    ],
)
