from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Base64UrlStr, Base64Str
from watermark.watermark import watermark_image, verify_watermark, string_to_binary

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
    watermarked_base64_image = watermark_image(base64_image, watermark_hash)
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