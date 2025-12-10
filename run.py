#!/usr/bin/env python3
"""
Startup script for watermark python API
"""
import os
import sys
from pathlib import Path

# Add api to path
# sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

if __name__ == "__main__":
  host = os.getenv("HOST", "0.0.0.0")
  port = int(os.getenv("PORT", 8000))

  uvicorn.run(
    "api.server:app",
    host=host,
    port=port,
    reload=os.getenv("ENV", "development") == "development"
  )