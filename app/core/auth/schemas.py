from typing import Optional

from pydantic import BaseModel


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: str

    def to_dict(self):
        return self.dict(exclude_unset=True)


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class JWTTokenData(BaseModel):
    username: str = None


class JWTTokenPayload(BaseModel):
    user_id: int = None


class Msg(BaseModel):
    msg: str
