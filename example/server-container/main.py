"""
This is the main entrypoint for the model serving app.
"""

import uvicorn
from fastapi import FastAPI
import inference as inf

# Initialize API
app = FastAPI()

# Add route for inference logic
app.include_router(
    inf.router,
    prefix='',
    tags=["inference"]
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
