from pydantic import BaseModel
from typing import List, Dict

class AssignRequest(BaseModel):
    participants: int
    rooms: int
    rounds: int

class AssignResponse(BaseModel):
    assignments: List[Dict[int, List[int]]]
