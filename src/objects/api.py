from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware 
import Pyro5.client
from actor import Actor
from activities import*
from post import Post
import json
from typing import Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from actor import Actor
from chordRing import ChordNode



# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "97af2450780e8090d64696b529c104c1aadbc356ecbed48feb4e2b7db4b42622"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Union[str, None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(node:ChordNode, id: str):
    user = node.search(id)
    return user


def authenticate_user(node:ChordNode, id: str, password: str):
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

    with json.load('servers.json') as servers:
        connect_server = servers[0]
        try:
            with Pyro5.client.Proxy('PYRO:actors@'+connect_server+':8002') as node:
                user = get_user(node=node, id=token_data.id)
        except:
            print('Error accediendo a usuarios')

    if user is None:
        raise credentials_exception
    return user


# async def get_current_active_user(current_user: Actor = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user=None
    with json.load('servers.json') as servers:
        connect_server = servers[0]
        try:
            with Pyro5.client.Proxy('PYRO:actors@'+connect_server+':8002') as node:
                user = authenticate_user(node, form_data.username, form_data.password)
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


# @app.get("/users/me/", response_model=Actor)
# async def read_users_me(current_user: Actor = Depends(get_current_user)):
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(current_user: Actor = Depends(get_current_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]


app = FastAPI()


# NEW
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:32020"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Welcome to Retex API! To view an evaluation of the model navigate to /eval. To search on the model navigate to /search?q=<msg>. To view a document navigate to /collection?doc_id=<id>"
    
@app.put("/create_user")
def create_user(username:str,alias:str,password:str):
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            if node.search(alias) is None:
                node.add(Actor(alias,username,get_password_hash(password)))
                
            else: raise HTTPException(status_code=400, detail=f"User {alias} already exist")
  
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    return 'success'
       
@app.post("/{alias}/change_password")
async def change_password(password:str,current_user: Actor = Depends(get_current_user)):
    current_user.hashed_password=get_password_hash(password=password)
    return 'success'
    
@app.post("/{alias}/post") 
async def create_post(post_dict:Dict,reply:str,current_user: Actor = Depends(get_current_user)):
    try:
        moment=datetime.now()
        post = Post(current_user.id+str(moment),current_user.id, post_dict.get('content'), reply, moment)
        ca = CreateActivity("Create"+post.id,post.author,post.id,post.published,current_user.followers,None)

        with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as node:
            node.add(post)

        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            node.search(current_user.outbox).add(ca)
        
        try:
            with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
                try:
                    with Pyro5.client.Proxy('PYRO:inboxes@172.28.5.1:8002') as inb:
                        for i in current_user.followers: 
                            act_i=node.search(i)
                            inb.search(act_i.intbox).add(ca)                   
                except: raise HTTPException(status_code=500,detail=f"An error has occurred")
        except: raise HTTPException(status_code=500,detail=f"An error has occurred")
                    
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

    return 'success'   
    
@app.get("/{alias}/following")
async def get_following(current_user: Actor = Depends(get_current_user)):
    following={}
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
        
            for i in current_user.following:
           
                usr=node.search(i)
                if usr is None: raise HTTPException(status_code=404, detail=f"Username {i} not found")
                    
                else:   
                    following[i]=usr
                    
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

    return following
            
@app.get("/{alias}/followers")
async def get_followers(current_user: Actor = Depends(get_current_user)):
    followers={}
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            for i in current_user.followers:
                    
                usr=node.search(i)
                if usr is None: 
                    raise HTTPException(status_code=404, detail=f"Username {i} not found")        
                else:   
                    followers[i]=usr                
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

    return followers

@app.get("/{alias}/posts")
async def get_posts(current_user: Actor = Depends(get_current_user)):
    posts=[]
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            usr_ob=node.search(current_user.outbox)

            with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as post_dht:
                for i in usr_ob.items:
                    if i.type=="CreateActivity":
                        posts.append(post_dht.search(i.obj))
                    elif i.obj.type=="ShareActivity":
                        posts.append((post_dht.search(i.obj),post_dht.search(i.obj_share)))
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

    return posts
       
@app.get("/{alias}/likes")
async def get_likes(current_user: Actor = Depends(get_current_user)):
    likes=[]
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            usr_ob=node.search(current_user.outbox)
            
            with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as post_dht:
                for i in usr_ob.items:
                    if i.type=="Like":
                        likes.append(post_dht.search(i.obj))
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    return likes
   
@app.put("/{alias}/{post}/like") 
async def like(post_data:Dict, current_user: Actor = Depends(get_current_user)):
    try:

        ca=LikeActivity("Like",current_user,post_data.get('id'))
        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            node.search(current_user.outbox).add(ca)
            
        with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as node:
            p=node.search(post_data.get('id'))
            p.like(current_user.id)
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

@app.put("/{alias}/{post}/share_post") 
async def share_post(post_dict:Dict,share_post:str,current_user: Actor = Depends(get_current_user)):
    try:
        moment=datetime.now()
        post = Post(current_user.id+str(moment),current_user.id, post_dict.get('content'), None, moment)
        with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as node:
            node.add(post)
        
        sa = ShareActivity("Share"+current_user.id+str(moment),post.id,share_post)
        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            node.search(current_user.outbox).add(sa)
        
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            for i in current_user.followers:                 
                act_i=node.search(i)
                try:
                    with Pyro5.client.Proxy('PYRO:inboxes@172.28.5.1:8002') as inb:
                        inb.search(act_i.inbox).add(sa)
                except: raise HTTPException(status_code=500,detail=f"An error has occurred")
                    
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
    return 'success'

@app.delete("/{alias}/{post}/delete_post")
async def delete_post(post_id:str,current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy('PYRO:posts@172.28.5.1:8002') as node:
            post=node.search(post_id)
            if post.author == current_user.id:
                #hacerle algo 
                ...
            else:
                raise HTTPException(status_code=401,detail=f"Unauthorized")

        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            ra = DeleteActivity('Delete'+post_id,post_id)
            node.add(ra)
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    return 'success'

async def unfollow(user_id,current_user: Actor = Depends(get_current_user)):
    del current_user.following[user_id]
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user = node.search(user_id)
            del user.followers[current_user.id]
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    try:
        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
            node.search(current_user.outbox).add(UnfollowActivity('Unfollow'+user_id,user_id))
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
        
    return 'success'   