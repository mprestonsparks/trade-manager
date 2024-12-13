"""Health check endpoints for trade manager service."""
from fastapi import APIRouter, Response, status
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
