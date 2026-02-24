from fastapi import APIRouter

router = APIRouter()


@router.post("/chirpstack")
async def chirpstack_webhook():
    """
    Webhook HTTP alternativo para ChirpStack.
    Úsalo si prefieres HTTP sobre MQTT.
    — próximamente.
    """
    return {"message": "Webhook endpoint - coming soon"}
