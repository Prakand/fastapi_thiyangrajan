from typing import Optional
from fastapi import FastAPI,Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app=FastAPI()


try:
    conn=psycopg2.connect(host='localhost',database='fastapidb',user='postgres',password='Mishra@2001',cursor_factory=RealDictCursor)
    cursor=conn.cursor()
    print('Established Connection Successfully')
    
except Exception as e:
    print('Error',e)
    

class Post(BaseModel):
    title:str
    content:str
    published:bool = True
    rating: Optional[int]=None



@app.get('/login')
def read_root():
    return {"message":"Hello Welcome to my api"}

@app.get('/post')
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts=cursor.fetchall()
    return {"message":posts}


@app.post('/post')
def post_req(post:Post):
    cursor.execute(""" INSERT INTO posts(title,content,published) VALUES(%s,%s,%s) RETURNING * """,
                   (post.title,post.content,post.published))
    new_post=cursor.fetchone()
    conn.commit()
    return {"message":new_post}


@app.get('/posts/{id}')
def get_one_post(id:int):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """,str(id))
    one_post=cursor.fetchone()
    return {"message":one_post}


@app.delete('/posts/{id}')
def post_delete(id:int):
    cursor.execute(""" DELETE FROM posts WHERE id=%s returning * """,str(id))
    del_post=cursor.fetchone()
    conn.commit()
    if del_post ==None:
        raise ValueError({"message":"this id does not exist"})
    return {"message":del_post}


@app.put('/posts/{id}')
def update_post(id:int,post:Post):
    cursor.execute("""UPDATE posts SET title = %s,content=%s,published=%s WHERE id=%s RETURNING * """,
                   (post.title,post.content,post.published,str(id)))
    resp=cursor.fetchone()
    conn.commit()
    if resp == None:
        raise ValueError({"message":"id doesn't match or exist"})
    return {"message":resp}
