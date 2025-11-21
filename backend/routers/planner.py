from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your route modules
from backend.routers.life_planner import router as full_planner_router
from backend.routers.lifeplanner3day import router as planner3day_router
from backend.routers.lifeplanner21day import router as planner21day_router

app = FastAPI(
    title="Perpetual Life Planner API",
    description="Routes for full, 21-day, and 3-day life planning endpoints.",
    version="1.0.0"
)

# CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all planner routers under the /planner prefix
app.include_router(full_planner_router, prefix="/planner")
app.include_router(planner3day_router, prefix="/planner")
app.include_router(planner21day_router, prefix="/planner")

@app.get("/")
def read_root():
    return {"message": "Perpetual Life Planner API is running!"}
