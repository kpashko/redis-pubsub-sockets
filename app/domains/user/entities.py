import bcrypt
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    name: str
    email: EmailStr


class User(UserBase):
    id: str
    password: str


class UserCreateDB(UserBase):
    password: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("password", mode="before")
    def hash_password(cls, value):
        pwd_bytes = value.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password


class UserAPIResponse(BaseModel):
    message: str = "User created successfully"
    user: None | UserBase = None


class UserAPICreate(UserBase):
    password: str
