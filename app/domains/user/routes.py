from fastapi import APIRouter, HTTPException, status

from app.api import ResponseErrorSchema
from app.domains.user import User, UserAPICreate, UserAPIResponse, UserCreateDB
from app.repositories.exceptions import AlreadyExistsException
from app.repositories.user import set_up_user_repository

router = APIRouter()


@router.post(
    "/",
    tags=["users"],
    response_model=UserAPIResponse,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ResponseErrorSchema,
            "detail": "User already exists",
        }
    },
)
async def create_user(user_data: UserAPICreate):
    try:
        async with set_up_user_repository() as repo:
            user = await repo.add(UserCreateDB(**user_data.dict()))
    except AlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    return UserAPIResponse(user=user)
