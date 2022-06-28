import uvicorn
import Pyro5.client
from .post import Post
from .actor import Actor
from typing import Union
from .activities import *
from copy import deepcopy
from jose import JWTError, jwt
from pydantic import BaseModel
from .cache import Cache, CacheItem
from .dht.chord_node import ChordNode
from .cache.cache import Cache,CacheItem
from copy import deepcopy
import numpy as np
from numpy import array
from random import randint, uniform
from .classifier.text_classifier import TextClassifier
import socket as sck
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

##Matrix
GRAPH = array([
    [1.0, 0.3, 0.4, 0.6, 0.2, 0.3, 0.5, 0.6, 0.8, 0.9],
    [0.1, 1.0, 0.2, 0.7, 0.8, 0.5, 0.7, 0.65, 0.5, 0.8],
    [0.78, 0.1, 1.0, 0.6, 0.2, 0.5, 0.2, 0.7, 0.65, 0.79],
    [0.6, 0.4, 0.2, 1.0, 0.2, 0.45, 0.3, 0.5, 0.8, 0.7],
    [0.18, 0.86, 0.4, 0.3, 1.0, 0.67, 0.56, 0.7, 0.4, 0.69],
    [0.2, 0.3, 0.6, 0.2, 0.1, 1.0, 0.5, 0.7, 0.3, 0.4],
    [0.7, 0.6, 0.3, 0.5, 0.6, 0.58, 1.0, 0.62, 0.48, 0.53],
    [0.8, 0.1, 0.2, 0.1, 0.8, 0.82, 0.458, 1.0, 0.23, 0.38],
    [0.6, 0.1, 0.7, 0.75, 0.4, 0.5, 0.64, 0.58, 1.0, 0.4],
    [0.9, 0.2, 0.4, 0.6, 0.3, 0.2, 0.86, 0.42, 0.21, 1.0]
])
##

##Classifier
CLASSIFIER=TextClassifier()
##


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "97af2450780e8090d64696b529c104c1aadbc356ecbed48feb4e2b7db4b42622"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CACHE = Cache(512)
IP: str = sck.gethostbyname(sck.gethostname())

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Union[str, None] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# NEW
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:32020"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(node: ChordNode, id: str):
    user = node.search(id)
    return user


def authenticate_user(node: ChordNode, id: str, password: str):
    user = get_user(node, id)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception

    user = None

    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user = get_user(node=node, id=token_data.id)
    except:
        print('Error accediendo a usuarios')

    if user is None:
        raise credentials_exception
    return user

@app.put("/forgot_password")
def forgot_password(alias:str,a1:str,a2:str,password:str):
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None: raise HTTPException(status_code=404, detail=f"Username {alias} not found")
            
            _a1=get_password_hash(a1)
            _a2=get_password_hash(a2)
            _password=get_password_hash(password)
            
            if user.forgot_password(_password,_a1,_a2):
                return "success"
            
            else:
                raise HTTPException(detail=f"An error has occurred")
    except:
        raise HTTPException(status_code=500,detail=f"The operation has faild")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user = authenticate_user(
                node, form_data.username, form_data.password)
    except:
        print('Error accediendo a usuarios')

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect alias or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}




@app.put("/create_user")
def create_user(username: str, alias: str, password: str):
    try:
        with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
            if node.search(alias) is None:
                node.add(Actor(alias, username, get_password_hash(password)))

            else:
                raise HTTPException(
                    status_code=400, detail=f"User {alias} already exist")

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    return 'success'


@app.post("/{current_user}/change_password")
async def change_password(password: str, current_user: Actor = Depends(get_current_user)):
    current_user.hashed_password = get_password_hash(password=password)
    return 'success'


@app.post("/{alias}/post")
async def create_post(content: str, reply: str, current_user: Actor = Depends(get_current_user)):
    try:
        moment=datetime.now()
        post = Post(current_user.id+str(moment),current_user.id, content, reply, moment)
        
        ca = CreateActivity("Create"+post.id,post.author,post.id,post.published,current_user.followers,None)

        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            node.add(post)

        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(ca)

        current_user.posts_soa += 1
        
        if reply is None:
            post.cat_label=CLASSIFIER.predict(content)
            
        else:
            try:
                with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
                    rp = node.search(reply)
                    rp._replies.append(post)
                
            except:
                raise HTTPException(
                        status_code=500, detail=f"An error has occurred")
        try:
            with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
                try:
                    with Pyro5.client.Proxy('PYRO:inboxes@{IP}:8002') as inb:
                        for i in current_user.followers:
                            act_i = node.search(i)
                            inb.search(act_i.intbox).add(ca)
                except:
                    raise HTTPException(
                        status_code=500, detail=f"An error has occurred")
        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred")

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    return 'success'


@app.get("/{alias}/following")
async def get_following(current_user: Actor = Depends(get_current_user)):
    if CACHE.is_in(f"{current_user.id}.following") and CACHE.get(f"{current_user.id}.following")[1] == current_user.following_soa:
        return CACHE.get(f"{current_user.id}.following")[0]

    else:
        following = {}
        try:
            with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:

                for i in current_user.following:

                    usr = node.search(i)
                    if usr is None:
                        raise HTTPException(
                            status_code=404, detail=f"Username {i} not found")

                    else:
                        following[i] = usr

        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred")

        if CACHE.is_in(f"{current_user.id}.following"):
            CACHE._memory[CACHE._hash(f"{current_user.id}.following")] = CacheItem(
                [deepcopy(following), current_user.following_soa])
        else:
            CACHE.add(key=f"{current_user.id}.following", value=[
                      deepcopy(following), current_user.following_soa])
        return following


@app.get("/{alias}/followers")
async def get_followers(current_user: Actor = Depends(get_current_user)):
    if CACHE.is_in(f"{current_user.id}.followers") and CACHE.get(f"{current_user.id}.followers")[1] == current_user.following_soa:
        return CACHE.get(f"{current_user.id}.followers")[0]

    else:
        followers = {}
        try:
            with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
                for i in current_user.followers:

                    usr = node.search(i)
                    if usr is None:
                        raise HTTPException(
                            status_code=404, detail=f"Username {i} not found")
                    else:
                        followers[i] = usr
        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred")

        if CACHE.is_in(f"{current_user.id}.followers"):
            CACHE._memory[CACHE._hash(f"{current_user.id}.followers")] = CacheItem(
                [deepcopy(followers), current_user.followers_soa])
        else:
            CACHE.add(key=f"{current_user.id}.followers", value=[
                      deepcopy(followers), current_user.followers_soa])
        return followers


@app.get("/{alias}/posts")
async def get_posts(current_user: Actor = Depends(get_current_user)):
    if CACHE.is_in(f"{current_user.id}.posts") and CACHE.get(f"{current_user.id}.posts")[1] == current_user.posts_soa:
        return CACHE.get(f"{current_user.id}.posts")[0]
    posts = []
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            usr_ob = node.search(current_user.outbox)

            with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items:
                    if i.type == "CreateActivity":
                        posts.append(post_dht.search(i.obj))
                    elif i.obj.type == "ShareActivity":
                        posts.append(
                            (post_dht.search(i.obj), post_dht.search(i.obj_share)))
    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    if CACHE.is_in(f"{current_user.id}.posts"):
        CACHE._memory[CACHE._hash(f"{current_user.id}.posts")] = CacheItem(
            [deepcopy(posts), current_user.posts_soa])
    else:
        CACHE.add(key=f"{current_user.id}.posts", value=[
                  deepcopy(posts), current_user.posts_soa])

    return posts


@app.get("/{alias}/likes")
async def get_likes(current_user: Actor = Depends(get_current_user)):
    if CACHE.is_in(f"{current_user.id}.likes") and CACHE.get(f"{current_user.id}.likes")[1] == current_user.likes_soa:
        return CACHE.get(f"{current_user.id}.likes")[0]
    likes = []
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            usr_ob = node.search(current_user.outbox)

            with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items:
                    if i.type == "Like":
                        likes.append(post_dht.search(i.obj))
    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    if CACHE.is_in(f"{current_user.id}.likes"):
        CACHE._memory[CACHE._hash(f"{current_user.id}.likes")] = CacheItem(
            [deepcopy(likes), current_user.likes_soa])
    else:
        CACHE.add(key=f"{current_user.id}.likes", value=[
                  deepcopy(likes), current_user.likes_soa])

    return likes


@app.put("/{alias}/{post_id}/like")
async def like(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:

        ca = LikeActivity("Like", current_user, post_id)
        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(ca)

        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            p = node.search(post_id)
            p.like(current_user.id)

        current_user.posts_soa += 1

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    
    current_user.info["likes"]+=1
    return 'success'


@app.put("/{alias}/{post_id}/share_post")
async def share_post(content: str, share_post: str, current_user: Actor = Depends(get_current_user)):
    try:
        moment = datetime.now()
        post = Post(current_user.id+str(moment),
                    current_user.id, content, None, moment)
        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            node.add(post)

        sa = ShareActivity("Share"+current_user.id +
                           str(moment), post.id, share_post)
        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(sa)

        with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
            for i in current_user.followers:
                act_i = node.search(i)
                try:
                    with Pyro5.client.Proxy('PYRO:inboxes@{IP}:8002') as inb:
                        inb.search(act_i.inbox).add(sa)
                        current_user.posts_soa += 1
                except:
                    raise HTTPException(
                        status_code=500, detail=f"An error has occurred")
                    
            try:
                with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
                    sp = node.search(share_post)
                    sp._shared.append(current_user.id)
                
            except:
                raise HTTPException(
                        status_code=500, detail=f"An error has occurred")

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    return 'success'


@app.delete("/{alias}/{post_id}/delete_post")
async def delete_post(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            post = node.search(post_id)
            if post.author == current_user.id:
                node.remove(post.id)
            else:
                raise HTTPException(status_code=401, detail=f"Unauthorized")

        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            ra = DeleteActivity('Delete'+post_id, post_id)
            current_user.posts_soa += 1
            node.add(ra)
    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    current_user.info["posts"]-=1
    return 'success'


@app.post("/{alias}/{user_id}/follow")
async def follow(user_id, current_user: Actor = Depends(get_current_user)):
    current_user.followin[user_id] = user_id
    current_user.followin_soa += 1
    try:
        with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
            user = node.search(user_id)

        try:
            with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as fol:
                fol.search(current_user.outbox).add(
                    FollowActivity('Follow'+user_id, user_id))
                user.followers[current_user.id] = current_user.id
                user.followers_sao += 1
        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred")

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    return 'success'


@app.delete("/{alias}/{user_id}/unfollow")
async def unfollow(user_id, current_user: Actor = Depends(get_current_user)):
    del current_user.following[user_id]
    current_user.followin_soa += 1
    try:
        with Pyro5.client.Proxy('PYRO:actors@{IP}:8002') as node:
            user = node.search(user_id)
            del user.followers[current_user.id]
            user.followers_soa += 1

            try:
                with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as fol:
                    fol.search(current_user.outbox).add(
                        UnfollowActivity('Unfollow'+user_id, user_id))
            except:
                raise HTTPException(
                    status_code=500, detail=f"An error has occurred")
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
        
    return 'success'   

@app.post("/{alias}/preferences")
async def set_preferences(preferences:list,current_user: Actor = Depends(get_current_user)):
    pref=[0 for i in range(10)]
    if len(preferences)>0:
        pref[preferences[0]]=uniform(0.8,1)
    
    if len(preferences)>1:
        pref[preferences[1]]=uniform(0.6,0.8)
        
    if len(preferences)>2:
        pref[preferences[2]]=uniform(0.5,0.6)
        
    if len(preferences)>3:
        pref[preferences[3]]=uniform(0.45,0.5)
        
    pref=array(pref)
    u_pref=np.dot(pref,GRAPH)
    current_user.preferences=u_pref
    return 'succes'


@app.put("/{alias}/{post_id}/unlike")
async def unlike(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@{IP}:8002') as node:
            for i in node.items:
                if i.type == "LikeActivity" and i.id==post_id:
                    node.remove(i)
                    break
            

        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            p=node.search(post_id)
            p.unlike(current_user.id)

        current_user.posts_soa += 1

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    
    
@app.get("/{alias}/info")
async def get_info(current_user: Actor = Depends(get_current_user)):
    info={}
    info["user_name"]=current_user.user_name
    info["alias"]=current_user.alias
    info["followers"]=len(current_user.followers)
    info["following"]=len(current_user.following)
    
    return info

@app.get("/{post}/get_shared_by")
async def get_info(post_id:str):
    try:
        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            sp = node.search(share_post)
            return sp._shared
            
        
    except:
        raise HTTPException(
                status_code=500, detail=f"An error has occurred")
        
@app.get("/{post}/get_likes")
async def get_info(post_id:str):
    try:
        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            sp = node.search(share_post)
            return sp._likes
            
        
    except:
        raise HTTPException(
                status_code=500, detail=f"An error has occurred")
        
@app.get("/{post}/get_replies")
async def get_info(post_id:str):
    try:
        with Pyro5.client.Proxy('PYRO:posts@{IP}:8002') as node:
            sp = node.search(share_post)
            return sp._replies
            
        
    except:
        raise HTTPException(
                status_code=500, detail=f"An error has occurred")

     