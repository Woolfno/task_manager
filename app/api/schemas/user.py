from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserIn(User):
    password: str
