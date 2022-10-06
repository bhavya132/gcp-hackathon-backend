from datetime import datetime
import json
from pydantic import BaseModel, validator
from hashlib import md5
from typing import List,Optional


class UserBase(BaseModel):
    email: str
    name: str
    display_picture: str
    score: int = 0
    plants:list
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str

    @validator('password', pre=True)
    def pw_creation(cls, v: str):
        if len(v) < 5:
            raise ValueError("Password too short")
        hashed_pw = md5(v.encode()).hexdigest()
        return hashed_pw


class UserLogin(BaseModel):
    email: str
    password: str

    @validator('password', pre=True)
    def pw_creation(cls, v: str):
        hashed_pw = md5(v.encode()).hexdigest()
        return hashed_pw


class TokenJWT(BaseModel):
    access_token: str
    refresh_token: str


class PlantPred(BaseModel):
    is_plant: bool
    pred_prob: float
    plant_name: str
    plant_image: str
    common_names: Optional[List[str]]
    species: str
    # more info
    url: str
    description: str
    # score: int


class SpeciesReq(BaseModel):
    image: str


class GarbageResp(BaseModel):
    result: str

# class Leaderboard(BaseModel):
#     result: json

# class UserScore(BaseModel):
#     userEmail: str
#     score: int
#     rank: int

class PlantationResp(BaseModel):
    score: int
    msg: str


class SchemasMsg(BaseModel):
    msg: str


