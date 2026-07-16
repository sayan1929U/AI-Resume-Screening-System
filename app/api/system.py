from fastapi import APIRouter
import psutil

router = APIRouter(tags=["System"])

@router.get("/system")
async def system_status():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }