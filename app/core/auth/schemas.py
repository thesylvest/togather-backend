from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    token: Optional[str] = None


class CredentialsSchema(BaseModel):
    username: Optional[str]
    password: str
    email: Optional[str] = None

    def to_dict(self):
        return self.dict(exclude_unset=True)


class JWTToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class Msg(BaseModel):
    msg: str
