from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .research_reports import router as reports_router

app = FastAPI(
    title="Medical Research Portal API",
    description="API for serving medical research reports",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports_router, prefix="/api", tags=["reports"])
