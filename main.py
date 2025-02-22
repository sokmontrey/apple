import requests
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

url = 'https://rn1ofmy-webendpoint.sandbox.landing.ai/inference'

class RequestJSON(BaseModel):
  image_path: str

@app.post("/inference/")
async def predict(image_path: RequestJSON):
  print(image_path)
  data = {
    'image_path': image_path,
  }

  headers = {
    "Authorization": "Basic bWxmaTlobG9iajQ1OG8weDhxNGFsOkVhck5EYWE1NDhQdURSQktmdnBsU3N5U1AxQXBuWVQz"
  }

  response = requests.post(url, data=data, headers=headers)
  return response.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)