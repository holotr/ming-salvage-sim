#!/usr/bin/env python3
"""Docker entrypoint for ming-salvage-sim web application.

Starts the FastAPI application with Uvicorn on port 8000.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
