from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from watermark.watermark import verify_watermark, string_to_binary
import requests
import json

class ImageSchema(BaseModel):
    base64_image: str
    watermark_hash: str


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Response:
    - status: "ok"
    - message: "Server is running"
    """
    return {
        "status": "ok",
        "message": "Server is running"
    }

@app.post("/watermark-image")
async def embed_watermark(
  image: ImageSchema
):
    base64_image = image.base64_image
    watermark_hash = image.watermark_hash
    
    # Make API call to LLM service for watermarking
    llm_api_url = "http://localhost:1234/v1/chat/completions"
    payload = {
        "model": "qwen/qwen3-vl-4b",
        "messages": [
            {
                "role": "user",
                "content": f"Watermark this image: {base64_image} using this hash: {watermark_hash}"
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "watermark_image",
                    "description": "Watermark a base64 encoded image with the provided unique identifier/hash. Call this whenever you need to watermark an image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base64_image": {
                                "type": "string",
                                "description": "The base64 encoded image to watermark.",
                            },
                            "watermark_hash": {
                                "type": "string",
                                "description": "The unique identifier/hash to use for watermarking. This is a unique identifier for the image that is used to watermark it.",
                            },
                        },
                        "required": ["base64_image", "watermark_hash"],
                        "additionalProperties": False,
                    },
                },
            }
        ]
    }
    
    try:
        response = requests.post(llm_api_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        result = response.json()
        
        # Extract the watermarked image from the LLM response
        # The response structure depends on how the LLM returns function call results
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "tool_calls" in choice["message"]:
                # If the LLM made a function call, we need to execute it or get the result
                # This assumes the LLM service executes the function and returns the result
                tool_call = choice["message"]["tool_calls"][0]
                if "function" in tool_call and "arguments" in tool_call["function"]:
                    # Parse the function arguments to get the result
                    # Note: This may need adjustment based on actual LLM API response format
                    watermarked_base64_image = json.loads(tool_call["function"]["arguments"]).get("result")
            elif "message" in choice and "content" in choice["message"]:
                # If the LLM returns the result in content
                watermarked_base64_image = choice["message"]["content"]
            else:
                watermarked_base64_image = None
        else:
            watermarked_base64_image = None
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to LLM service: {str(e)}"
        )
    
    if watermarked_base64_image is None:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to watermark image")
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "success": True,
        "message": "Image watermarked successfully",
        "watermarked_base64_image": watermarked_base64_image
    })

@app.post("/verify-watermark")
async def verify_watermark_endpoint(
  image: ImageSchema
):
    base64_image = image.base64_image
    watermark_hash = image.watermark_hash
    verified = verify_watermark(base64_image, watermark_hash)
    if verified:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "message": "Image verified successfully"})
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image verification failed")



@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Image Watermarking Backend API",
        "version": "1.0.0",
        "status": "running"
    }