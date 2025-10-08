
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from life_planner import router as planner_router

app = FastAPI(
    title="Perpetual Life Planner API",
    version="1.0.0",
    description="Provides roadmap planning for 3-day, 21-day, and full planners."
)

# Enable CORS for frontend (React on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all planner endpoints at /planner
app.include_router(planner_router, prefix="/planner")

@app.get("/")
def read_root():
    return {"message": "Perpetual Life Planner API is running"}
