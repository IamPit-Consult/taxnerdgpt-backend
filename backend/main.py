from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local router imports
from routers.life_planner import router as full_planner_router
from routers.lifeplanner3day import router as planner3day_router
from routers.lifeplanner21day import router as planner21day_router
from routers.reminders_router import router as reminders_router

# Optional email router (if present)
try:
    from routers.email_router import router as email_router
except ImportError:
    email_router = None


app = FastAPI(title="TaxNerdGPT Life Planner API")

# CORS – update domains as needed
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://taxnerd.us",
    "https://www.taxnerd.us",
    "https://app.taxnerd.us",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "TaxNerdGPT backend is running"}


# Routers
app.include_router(
    full_planner_router,
    prefix="/planner",
    tags=["full_planner"],
)

app.include_router(
    planner3day_router,
    prefix="/planner",
    tags=["planner_3day"],
)

app.include_router(
    planner21day_router,
    prefix="/planner",
    tags=["planner_21day"],
)

app.include_router(
    reminders_router,
    prefix="/reminders",
    tags=["reminders"],
)

if email_router is not None:
    app.include_router(
        email_router,
        prefix="/email",
        tags=["email"],
    )
