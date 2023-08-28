from typing import Optional

from pydantic import BaseModel


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[str] = None
    password: str

    def to_dict(self):
        return self.dict(exclude_unset=True)


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class Msg(BaseModel):
    msg: str
