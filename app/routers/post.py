from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from .. import models,schemas,oauth2
from sqlalchemy.orm import Session
from typing import Optional,List
from ..database import get_db
from sqlalchemy import func

router=APIRouter(prefix="/posts",tags=['Posts'])
@router.get("/",response_model=List[schemas.PostOut])
async def get_posts(db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user),limit:int=3,
                    skip:int=0,search:Optional[str]=""):
    #cursor.execute("""SELECT * FROM POSTS""")
    #posts=cursor.fetchall()
    #print(limit)
    #posts=db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts=db.query(models.Post,func.count(models.Votes.post_id).label("votes")).join(
        models.Votes,models.Votes.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts
    #print(posts)
    #return {"data":posts}
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post:schemas.PostCreate,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
   # cursor.execute("""INSERT INTO posts(title,content,published) VALUES (%s,%s,%s) RETURNING * """,(post.title,post.content,post.published))
    #new_post=cursor.fetchone()
    #conn.commit()
    #new_post=models.Post(title=post.title,content=post.content,published=post.published)
    print(current_user.email)
    post_dict = post.model_dump()
    new_post = models.Post(owner_id=current_user.id,**post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id:int,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #try:
        #cursor.execute("""SELECT * from posts where id=%s""",(id,))
        #post=cursor.fetchone()
        #if not post:
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                #detail=f"post with id: {id} was not found")
            #response.status_code=status.HTTP_404_NOT_FOUND
            #return {'message':f"post with id: {id} was not found"}
        
        #return{"post_detail":post}
    #except Exception as e:
        #conn.rollback()  # Rollback to clear any failed transaction
        #raise HTTPException(
            #status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #detail="Database query failed."
        #)
        post=db.query(models.Post,func.count(models.Votes.post_id).label("votes")).join(
        models.Votes,models.Votes.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first()
        #print(post)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with id: {id} was not found")
        return post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session=Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    #cursor.execute("""DELETE FROM posts where id=%s returning *""",(id,))
    #deleted_post=cursor.fetchone()
    #conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    deleted_post=post_query.first()
    if post_query.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} does not exist")
    if deleted_post.owner_id!=user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post)
def update_post(id:int,updated_post:schemas.PostCreate,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #cursor.execute("""UPDATE posts SET title=%s,content=%s,published=%s where id=%s returning *""",(post.title,post.content,post.published,(id,)))
    #updated_post=cursor.fetchone()
    #conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    updated_data=post_query.first()
    if updated_data ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not exist")
    #post_query.update({'title':'hey this is my updated title','content':'this is my updated content'},synchronization_session=False)
    if updated_data.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    post_query.update(updated_post.model_dump(),synchronize_session=False)
    db.commit()
    
    return post_query.first()