from google import genai
from google.genai import types
from pydantic import BaseModel, TypeAdapter
from fastapi import FastAPI
import os
import uvicorn

app = FastAPI()
import requests

class Apple(BaseModel):
  qualities: list[int]

class RequestJSON(BaseModel):
    image_path: str


@app.post("/check-apples")
async def call_ai_api(image_path: RequestJSON):
    path = image_path.image_path
    prompt = """Analyze the image to detect the number of apples present. Assess the quality of each apple based on the assigning a score from 0 to 10 (where 10 represents the highest quality and 0 represents the lowest)"""

    image = requests.get(path)
    
    GENAI_API_KEY = os.getenv("GENAI_API_KEY")

    client = genai.Client(api_key=GENAI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt,
                genai.types.Part.from_bytes(data=image.content, mime_type="image/jpeg")],
        config = {
            'response_mime_type': 'application/json',
            'response_schema': list[Apple],
        })
    apples: list[Apple] = response.parsed
    print(apples)
    return apples[0]


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)