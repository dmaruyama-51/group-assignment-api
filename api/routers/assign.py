from fastapi import APIRouter
from api.schemas.assign import AssignRequest, AssignResponse
from api.services.assigner import GreedyAssigner, RandomAssigner

router = APIRouter(prefix="/assign", tags=["assign"])


@router.post("/greedy", response_model=AssignResponse)
async def assign_greedy(request: AssignRequest) -> AssignResponse:
    assigner = GreedyAssigner(
        total_participants=request.participants,
        total_rooms=request.rooms,
        total_rounds=request.rounds,
    )
    assignments = assigner.generate_assignments()
    return AssignResponse(assignments=assignments)


@router.post("/random", response_model=AssignResponse)
async def assign_random(request: AssignRequest) -> AssignResponse:
    assigner = RandomAssigner(
        total_participants=request.participants,
        total_rooms=request.rooms,
        total_rounds=request.rounds,
    )
    assignments = assigner.generate_assignments()
    return AssignResponse(assignments=assignments)
