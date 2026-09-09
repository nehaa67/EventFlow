from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.events import router as events_router
from app.api.state import router as state_router
from app.api.predictions import router as predictions_router
from app.api.risk import router as risk_router
from app.api.causes import router as causes_router
from app.api.interventions import router as interventions_router
from app.api.simulation import router as simulation_router
from app.api.accommodation import router as accommodation_router

app = FastAPI(
    title="EventFlow AI",
    version="0.1.0",
    description="AI-powered mega-event crowd and capacity management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(state_router)
app.include_router(predictions_router)
app.include_router(risk_router)
app.include_router(causes_router)
app.include_router(interventions_router)
app.include_router(simulation_router)
app.include_router(accommodation_router)

@app.get("/")
def root():
    return {
        "message": "EventFlow AI backend is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    import traceback
    traceback.print_exc()

    return {
        "error": type(exc).__name__,
        "detail": str(exc),
    }