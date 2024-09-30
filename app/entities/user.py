from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
import bcrypt


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserAPIResponse(BaseModel):
    id: str
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password", mode="before")
    def hash_password(cls, value):
        pwd_bytes = value.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password
