from fastapi import APIRouter
from pydantic import BaseModel

from app.entities.user import UserAPIResponse, UserCreate
from app.repositories.exceptions import AlreadyExistsException
from app.repositories.user import set_up_user_repository

router = APIRouter()


class UserResponse(BaseModel):
    message: str = "User created successfully"
    user: None | UserAPIResponse = None


@router.post("/", tags=["users"], response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        async with set_up_user_repository() as repo:
            user = await repo.add(user_data)
    except AlreadyExistsException as exc:
        return UserResponse(message=str(exc))
    return UserResponse(user=UserAPIResponse.model_validate(user))
