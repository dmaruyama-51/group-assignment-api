from fastapi import APIRouter

router = APIRouter(
    prefix="/assign",
    tags=["assign"]
)

@router.post("/greedy")
async def assign_greedy():
    return {"message": "Greedy assignment"}

@router.post("/random")
async def assign_random():
    return {"message": "Random assignment"}