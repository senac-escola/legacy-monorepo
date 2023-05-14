from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
def hello_world():
    return {'Hello': 'World'}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/users/', response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_email=user.user_email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email já utilizado!')
    return crud.create_user(db=db, user=user)


@app.get('/users/', response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get('/users/{user_email}', response_model=schemas.UserRead)
def read_user(user_email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    return db_user


@app.patch('/users/{user_email}', response_model=schemas.UserRead)
def update_hero(
    user_email: str, user: schemas.UserUpdate, db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    return crud.update_user(db=db, db_user=db_user, user=user)


@app.delete('/users/{user_email}')
def delete_user(user_email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    return crud.delete_user(db=db, db_user=db_user)
