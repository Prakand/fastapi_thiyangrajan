from typing import Optional,List
from fastapi import FastAPI,Body,Depends,HTTPException,status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from .database import engine,get_db
from sqlalchemy.orm import Session
from app import models
from . import models,schemas



models.Base.metadata.create_all(bind=engine)

app=FastAPI()



try:
    conn=psycopg2.connect(host='localhost',database='fastapidb',user='postgres',password='Mishra@2001',cursor_factory=RealDictCursor)
    cursor=conn.cursor()
    print('Established Connection Successfully')
    
except Exception as e:
    print('Error',e)
    


@app.get('/login')
def read_root():
    return {"message":"Hello Welcome to my api"}

@app.get('/post',response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts=cursor.fetchall()
    posts=db.query(models.Post).all()
    return posts


@app.post('/post',response_model=schemas.Post)
def post_req(post:schemas.PostCreate,db: Session = Depends(get_db)):
    # cursor.execute(""" INSERT INTO posts(title,content,published) VALUES(%s,%s,%s) RETURNING * """,
    #                (post.title,post.content,post.published))
    # new_post=cursor.fetchone()
    # conn.commit()
    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get('/posts/{id}',response_model=schemas.Post)
def get_one_post(id:int,db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """,str(id))
    # one_post=cursor.fetchone()
    one_post=db.query(models.Post).filter(models.Post.id==id).first()
    if not one_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return one_post


@app.delete('/posts/{id}')
def post_delete(id:int,db: Session = Depends(get_db)):
    # cursor.execute(""" DELETE FROM posts WHERE id=%s returning * """,str(id))
    # del_post=cursor.fetchone()
    # conn.commit()
    del_post=db.query(models.Post).filter(models.Post.id==id)
    
    if del_post.first==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    del_post.delete(synchronize_session=False)
    db.commit()
    return del_post


@app.put('/posts/{id}',response_model=schemas.Post)
def update_post(id:int,updated_post:schemas.PostCreate,db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s,content=%s,published=%s WHERE id=%s RETURNING * """,
    #                (post.title,post.content,post.published,str(id)))
    # resp=cursor.fetchone()
    # conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post=post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} does not exists")
    post_query.update(updated_post.model_dump(),synchronize_session=False)
    db.commit()
    return post_query.first()

@app.post('/user',status_code=status.HTTP_201_CREATED)
def create_user(user:schemas.UserCreate,db: Session = Depends(get_db)):
    new_user=models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/users',status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users=db.query(models.User).all()
    return users
