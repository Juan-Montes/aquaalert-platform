from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_alerts():
    """Historial de alertas — próximamente."""
    return {"message": "Alerts endpoint - coming soon"}
