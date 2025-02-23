import os
import math
import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from google import genai
from google.genai import types

app = FastAPI()

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Apple(BaseModel):
    qualities: list[int]

class RequestJSON(BaseModel):
    image_path: str

class AppleQuality(BaseModel):
    quality_name: Optional[str] = None
    expiration_day: Optional[str] = None
    price: Optional[str] = None

def get_genai_client():
    """Helper function to initialize the GenAI client."""
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        raise ValueError("GENAI_API_KEY is not set.")
    return genai.Client(api_key=api_key)

def calculate_avg_score(qualities_list: list[int]) -> int:
    """Helper function to calculate the average score of qualities."""
    return math.floor(sum(qualities_list) / len(qualities_list)) if qualities_list else 0

def determine_apple_quality(avg_score: int) -> AppleQuality:
    """Helper function to determine the apple quality based on the average score."""
    result = AppleQuality()
    
    if 8 <= avg_score <= 10:
        result.quality_name = "Farm Fresh"
        result.expiration_day = "21 - 28 days"
        result.price = "{:.2f}".format(avg_score * 0.3) 
    elif 5 <= avg_score <= 7:
        result.quality_name = "Beauty in the Bite"
        result.expiration_day = "7 - 14 days"
        result.price = "{:.2f}".format(avg_score * 0.3) 
    else:
        result.quality_name = "ReFruit"
        result.expiration_day = "1 - 2 days"
        result.price = "Free"
    
    return result

@app.post("/check-apples/")
async def call_ai_api(image_path: RequestJSON):
    """Main API endpoint to process the apple quality based on an image."""
    try:
        # Get the image and prompt data
        image = requests.get(image_path.image_path)
        prompt = """Analyze the image to detect the number of apples present. Assess the quality of each apple based on the assigning a score from 0 to 10 (where 10 represents the highest quality and 0 represents the lowest)"""

        # Initialize the GenAI client
        client = get_genai_client()

        # Generate response using GenAI API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt, genai.types.Part.from_bytes(data=image.content, mime_type="image/jpeg")],
            config={'response_mime_type': 'application/json', 'response_schema': list[Apple]},
        )

        apples: list[Apple] = response.parsed

        if not apples:
            return {"error": "No apple data found in the response."}

        # Calculate the average score
        avg_score = calculate_avg_score(apples[0].qualities)
        print(f"Average Score is: {avg_score}")

        # Determine the apple quality based on the average score
        result = determine_apple_quality(avg_score)
        
        print(f"Result is {result}")

        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
