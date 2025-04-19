from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from passlib.context import CryptContext
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User operations
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Message operations
@app.post("/users/{user_id}/messages/", response_model=schemas.Message)
def create_message(user_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_message = models.Message(**message.dict(), user_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = db.query(models.Message).offset(skip).limit(limit).all()
    return messages

@app.get("/messages/{message_id}", response_model=schemas.Message)
def read_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@app.put("/messages/{message_id}", response_model=schemas.Message)
def update_message(message_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    for key, value in message.dict().items():
        setattr(db_message, key, value)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}
