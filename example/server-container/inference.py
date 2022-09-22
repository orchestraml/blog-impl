#!/usr/bin/env python3

import pandas as pd
import numpy as np
from fastapi import APIRouter
from orchestralib import OrchestraClient

router = APIRouter()

orchestra = OrchestraClient(
    api_key="74738ff5-5367-5958-9aee-98fffdcd1876",
    organization="novuslabs",
    environment="production-serving",
)

# auto filled in by Orchestra
model_obj = orchestra.get_model("cc-fraud-xgb")


def predict(transformed_data: pd.DataFrame):
    # Make Predictions
    score = model_obj.predict(transformed_data.values)

    return score


@router.post("/inference", status_code=200)
@orchestra.log_model_serving_code("serving-execution")
def inference(data: dict):
    # some code to validate the dict against the schema
    orchestra.validate_inputs(data)

    features = orchestra.get_features(data)
    predicted_score = predict(features)

    # all of `data` is already logged!
    orchestra.log_prediction(predicted_score)

    # TODO: format properly to the output_features of the model
    return predicted_score
