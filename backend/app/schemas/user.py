from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class RoleEnum(str, Enum):
    admin = "admin"
    supervisor = "supervisor"
    operator = "operator"


class UserBase(BaseModel):
    username: str
    role: RoleEnum


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    username: str
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)
