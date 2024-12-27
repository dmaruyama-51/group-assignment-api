from fastapi import APIRouter
from api.schemas.assign import AssignRequest

router = APIRouter(
    prefix="/assign",
    tags=["assign"]
)

@router.post("/greedy")
async def assign_greedy(request: AssignRequest):
    return {"message": "Greedy assignment"}

@router.post("/random")
async def assign_random(request: AssignRequest):
    return {"message": "Random assignment"}