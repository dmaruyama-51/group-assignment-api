from fastapi import APIRouter, HTTPException
from api.schemas.assign import AssignRequest, AssignResponse
from api.services.assigner import GreedyAssigner, RandomAssigner
from api.validators.assign import validate_assignment_request

router = APIRouter(prefix="/assign", tags=["assign"])


@router.post("/greedy", response_model=AssignResponse)
async def assign_greedy(request: AssignRequest) -> AssignResponse:
    try:
        validate_assignment_request(
            participants=request.participants,
            rooms=request.rooms,
            rounds=request.rounds,
        )
        assigner = GreedyAssigner(
            total_participants=request.participants,
            total_rooms=request.rooms,
            total_rounds=request.rounds,
        )
        assignments = assigner.generate_assignments()
        return AssignResponse(assignments=assignments)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.post("/random", response_model=AssignResponse)
async def assign_random(request: AssignRequest) -> AssignResponse:
    try:
        validate_assignment_request(
            participants=request.participants,
            rooms=request.rooms,
            rounds=request.rounds,
        )
        assigner = RandomAssigner(
            total_participants=request.participants,
            total_rooms=request.rooms,
            total_rounds=request.rounds,
        )
        assignments = assigner.generate_assignments()
        return AssignResponse(assignments=assignments)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")
