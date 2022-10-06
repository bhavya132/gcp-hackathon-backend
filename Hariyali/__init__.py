from io import BytesIO

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Generator
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

from Hariyali.Database import SessionLocal, engine
from Hariyali.Database import models
from Hariyali import schemas
from Hariyali import crud
from Hariyali.utils.speciesNew import identify_plant, get_species_from_src, get_score
from Hariyali.utils.faceVerifier import FaceVerifier
from Hariyali.utils.basic import save_image_local, cloud_storage
from Hariyali.utils.garbagePredictor import gp
from Hariyali.utils.getLeaderboard import getLeaderboard
import base64
import uuid
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/")
def index() -> str:
    return "hello world"


@app.post("/signup", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # db_user = crud.get_user_by_email(db, user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    user_added = crud.create_user(db=db, user=user)
    return schemas.UserBase.from_orm(user_added)


@app.post('/login', response_model=schemas.TokenJWT)
def login(user: schemas.UserLogin, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    print(db_user.display_picture)
    if db_user and db_user.password == user.password:
        token = schemas.TokenJWT.construct(
            access_token=authorize.create_access_token(subject=user.email, expires_time=False),
            refresh_token=authorize.create_refresh_token(subject=user.email)
        )
        return token
    else:
        raise HTTPException(status_code=401, detail="Invalid Email or password")


@app.post('/refresh')
def refresh(authorize: AuthJWT = Depends()):
    """
    follow login response type and docs here (https://indominusbyte.github.io/fastapi-jwt-auth/usage/refresh/ )
    """
    authorize.jwt_refresh_token_required()
    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(current_user)
    # No way to get the refresh token here.
    return {"access_token":new_access_token}


@app.get('/user', response_model=schemas.UserBase)
def get_user(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    """
    get user from token follow https://indominusbyte.github.io
    """
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    user_db: models.User = db.query(models.User).filter(models.User.email == current_user).first()
    if user_db is None:
        raise HTTPException(status_code=500, detail="Bug in Database")
    print(user_db.plants)
    user = schemas.UserBase.from_orm(user_db)
    print(user)
    return user

@app.get('/leaderboard')
def get_leaderboard(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):  
    authorize.jwt_required()
    data=getLeaderboard(db)
    # result = schemas.Leaderboard(data)
    return data

@app.delete('/user', response_model=schemas.SchemasMsg)
def del_user(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    user_db: models.User = crud.get_user_by_email(db, current_user)
    if user_db is None:
        raise HTTPException(status_code=500, detail="Bug in Database")
    crud.delete_user(db, user_db)
    return schemas.SchemasMsg(msg="User Deleted Successfully")


@app.post('/species', response_model=schemas.PlantPred)
async def get_species(img_req: schemas.SpeciesReq, authorize: AuthJWT = Depends()):
    """
    Get all the information about a plant image
    """
    authorize.jwt_required()
    try:
        # image = await request.body()
        pred = identify_plant(img_req.image)
        # print(pred, "=========================================")
        suggested = pred["suggestions"][0]

        # Construct the response Model
        resp = schemas.PlantPred.construct(
            is_plant=pred.get("is_plant", False),
            pred_prob=suggested.get("probability", 0.0),
            plant_name=suggested.get("plant_name", ""),
             plant_image=suggested["plant_details"].get(
                "wiki_image", {"value": ""}).get("value", ""),
            common_names=suggested["plant_details"].get("common_names", []),
            species=suggested["plant_details"].get("scientific_name", ""),
            url=suggested["plant_details"].get("url", ""),
           
            description=suggested["plant_details"].get(
                "wiki_description", {"value": ""}
            ).get("value", "")
        )
        # score = getScore(resp.plant_name)
        print(resp)
        return resp 

    except Exception as e:
        return HTTPException(500, detail=f"Plant ID API Down {e}")


@app.post('/plantation', response_model=schemas.PlantationResp)
def plantation(img_req: schemas.SpeciesReq, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    """
    Get points by uploading the image of plant you planted
    The image should contain your face (showing you and your plant in one image)
    """
    authorize.jwt_required()
    image = img_req.image
    current_user_email = authorize.get_jwt_subject()
    user_db: models.User = crud.get_user_by_email(db, current_user_email)
    loc = f'plantation_img_{uuid.uuid4()}.jpg'
    file_loc = save_image_local(loc, image)
    is_match = FaceVerifier(file_loc, user_db.display_picture).is_face_same()
    if is_match is not True:
        resp = schemas.PlantationResp.construct(
            score=0,
            msg='Face can`t be verified'
        )
    else:
        try:
            pred = identify_plant(image)
            suggested = pred["suggestions"][0]
            plant_name = suggested.get("plant_name", "")
            common_names = suggested["plant_details"].get("common_names", [''])[0]
            species = suggested["plant_details"]["scientific_name"]
            description = suggested["plant_details"].get(
                "wiki_description", {"value": ""}
            ).get("value", "")
            public_link = cloud_storage.upload(file_loc, loc)
            scores = get_score(species, user_db)
            plant = models.Plant(
                name=plant_name,
                species=species,
                common_species=common_names,
                image=public_link,
                description=description,
                score=scores
            )
            user_db.plants.append(plant)
            user_db.score = user_db.score + scores
            user_db.save_to_db(db)
            resp = schemas.PlantationResp.construct(
                score=scores,
                msg=f'you claimed {scores} points'
            )
        except Exception as e:
            # cloud_storage.delete(loc)
            resp = HTTPException(500, detail=f"Something went wrong {e}")

    os.remove(file_loc)
    print(resp)
    return resp


@app.post('/classify', response_model=schemas.GarbageResp)
def classify(img_req: schemas.SpeciesReq, authorize: AuthJWT = Depends()):
    """
    Is item recyclable
    """
    authorize.jwt_required()
    # bytes_img = BytesIO(base64.b64decode(img_req.image))
    loc = f'garbage_img_{uuid.uuid4()}.jpg'
    file_loc = save_image_local(loc, img_req.image)
    print(file_loc)
    return schemas.GarbageResp.construct(
        result=gp.classify(file_loc)
    )





#during artitechture, 7 different types of databases- which database and which artitechture should be uses--
## if mentioned then extra time
##checkout cloud reference artitechture to see different type of industries at different scales
## priyanka videos for making different gcp applications, articles on artitechtures
