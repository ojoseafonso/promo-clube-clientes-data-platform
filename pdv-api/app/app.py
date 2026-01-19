from fastapi import APIRouter

router = APIRouter(prefix="/pdv")

@router.get("/health")
def health():
    return {"status": "ok"}
