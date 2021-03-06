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
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from base64 import b64decode
import logging

# get logger from logging module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s -> %(message)s', "%d-%m-%Y %H:%M:%S")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

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
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
CACHE = Cache(512)
MAX_SAVE=2048
IP: str = sck.gethostbyname(sck.gethostname())

key=RSA.import_key('-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQCyiZht8PYKDNR0VNQKzmBD1s44BSsEKTjQyyoFZFZqU0oGmpP3\nht6wqVMV1VCyCNf9E3s3tzNgD5IkDg6wDC4rculcx2yQ7GsfSnU49/+yu2WoBF5J\nHzDcsWEJe9KmeNTp988JxeBjxtmORGLCfFLYDxiOU7VVPCo98nm16PkSmQIDAQAB\nAoGAGVeTleNyoRmSHJMf6ArEOkzmx6fgI76QLH7yD4LfC0eYRdiyMRvpRy05uGsn\ngaXktq0Ju+5asgNzzH9cUVvhP5dAAaTIeBB0NcwFDNO7KKwd6azwOKX7vjR8XaD3\nqAItIVwN7cvTZ08qelxuFlg+7fiUI1Ij45lXv9+oQhYt0BMCQQC4twFbmXBzoGrT\nQ+pWNWXSSE2OKAOck6UCOaLtZ/Gsnv/DjOG41zPhFQQX7UsqDJvSbvrAk/BH4aGX\n8LmN3Xh/AkEA93BK6lCesSvzr27RQl3nYjY5Eirx4voCDmIVL5AlrGh0Eliy8tFt\nzPqBNHDgZTbG8t2scdcAqrbnI/JS2fKo5wJBALgseKUdc9tGSt1FbWTxrwmhX/rq\n+Nbo+/EhCMvQBU9J5djUIshLgwXdD4zP5E8T7VY/o7Pajg0N8zJtKoZCGf8CQDWq\nbzUewyxeAf48pLomL7cHV51vHwNBggyojTvBocog5XvNLRKpBY19j2RWTvTkyoWG\nOo5+OTDNdpg/SGTo0mUCQAM5UVtFvO7wNId/RZuuOBc+176LWvuPHnbRq1BRr7M9\nNMYIfsf1q0hBNCKEMO8SUZ+dNPkNdqtgambqZUw9Wn0=\n-----END RSA PRIVATE KEY-----')
cipher=PKCS1_OAEP.new(key,hashAlgo=SHA256)

def my_decrypt(message:str)->str:
    return cipher.decrypt(b64decode(message + str(b'==')))
    
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
    allow_origins=["*"],
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
    print(user)
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

@app.head("/")
def root():
    logger.info('Server active')
    return "OK"

@app.get("/system_network")
def get_system_network():
    system = []
    with Pyro5.client.Proxy(f'PYRO:admin@{IP}:8002') as node:
        system = list(node.system_network)
    logger.info('System network: {}'.format(system))
    return system

@app.put("/forgot_password")
def forgot_password(alias:str, a1:str, a2:str, password:str):
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
            
            _a1=get_password_hash(my_decrypt(a1))
            _a2=get_password_hash(my_decrypt(a2))
            _password=get_password_hash(my_decrypt(password))
            
            if user.forgot_password(_password,_a1,_a2):
                return "success"
            
            else:
                raise HTTPException(status_code=500, detail=f"An error has occurred")
    except:
        raise HTTPException(status_code=500,detail=f"The operation has fail")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    d_password = my_decrypt(form_data.password)
    user = None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user = authenticate_user(
                node, form_data.username, d_password)
    except:
        print('Error accediendo a usuarios')
    print(user)
    if user is None or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect alias or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    logger.info('Token generated to {}'.format(user.alias))
    return {"access_token": access_token, "token_type": "bearer"}

@app.put("/create_user")
def create_user(username: str, alias: str, password: str, a1: str, a2: str):
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            item= node.search(alias)
            if item is None:
                node.add("Actor",(alias, username, get_password_hash(my_decrypt(password)), get_password_hash(my_decrypt(a1)), get_password_hash(my_decrypt(a2))))
                logger.info('User created: {}'.format(alias))
            else:
                raise HTTPException(
                    status_code=400, detail=f"User {alias} already exist")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has occurred {e}")


@app.post("/me/change_password")
async def change_password(password: str, current_user: Actor = Depends(get_current_user)):
    current_user.hashed_password = get_password_hash(password=my_decrypt(password))
    return 'success'


@app.post("/me/post")
async def create_post(content: str, reply: str = "", current_user: Actor = Depends(get_current_user)):
    try:
        moment=datetime.now()
        post = Post(current_user.id+str(moment),current_user.id, content, reply, moment)
        if reply == "":
            # classify post
            post.cat_label=CLASSIFIER.predict(content)
        else:
            try:
                # search original post and add reply
                with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
                    rp = node.search(reply)
                    if rp is None:
                        raise HTTPException(status_code=404, detail="Original post unreachable")
                    rp.add_reply(post.id)
                    rp.replies_soa += 1
                    rp.replies_soa %= MAX_SAVE
            except Exception as e:
                raise HTTPException(
                        status_code=500, detail=f"An error has occurred {e} !!!")

        # save new post
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            node.add("Post",(current_user.id+str(moment),current_user.id, content, reply, moment))
            p = node.search(current_user.id+str(moment))
            p.cat_label = post.cat_label
            current_user.posts_soa += 1
            current_user.posts_soa %= MAX_SAVE
        # put in outbox of current actor
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add("CreateActivity",("Create"+post.id,post.author,post.id,post.published,current_user.followers,post.reply))

        try:
            with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
                try:
                    with Pyro5.client.Proxy(f'PYRO:inboxes@{IP}:8002') as inb:
                        for i in current_user.followers:
                            act_i = node.search(i)
                            inb.search(act_i.inbox).add("CreateActivity",("Create"+post.id,post.author,post.id,post.published,current_user.followers,post.reply))
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"An error has occurred {e} ...")
        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred: {e} -")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error has occurred: {e} %")

    return 'success'


@app.get("/{alias}/followings")
async def get_following(alias: str, current_user: Actor = Depends(get_current_user)):
    user=None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"User {alias} not found")
    except:
       raise HTTPException(
                status_code=500, detail=f"An error has occurred")
        
    if user!=None and CACHE.is_in(f"{user.id}.following") and CACHE.get(f"{user.id}.following")[1] == user.following_soa:
        return CACHE.get(f"{user.id}.following")[0]

    else:
        following = []
        try:
            with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
                for i in user.following:
                    usr = node.search(i)
                    if usr is None:
                        raise HTTPException(
                            status_code=404, detail=f"Username {i} not found")
                    else:
                        following.append({"username": usr.user_name, "alias": usr.alias})
        except:
            raise HTTPException(status_code=500, detail=f"An error has occurred")

        if CACHE.is_in(f"{user.id}.following"):
            CACHE._memory[CACHE._hash(f"{user.id}.following")] = CacheItem(
                [deepcopy(following), user.following_soa])
        else:
            CACHE.add(key=f"{user.id}.following", value=[
                      deepcopy(following), user.following_soa])
        return following


@app.get("/{alias}/followers")
async def get_followers(alias: str,  current_user: Actor = Depends(get_current_user)):
    user=None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"User {alias} not found")
    except:
       raise HTTPException(status_code=500, detail=f"An error has occurred")
    
    if user!=None and CACHE.is_in(f"{user.id}.followers") and CACHE.get(f"{user.id}.followers")[1] == user.followers_soa:
        return CACHE.get(f"{user.id}.followers")[0]
    else:
        followers = []
        try:
            with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
                for i in user.followers:
                    usr = node.search(i)
                    if usr is None:
                        raise HTTPException(status_code=404, detail=f"Username {i} not found")
                    else:
                        followers.append({"username": usr.user_name, "alias": usr.alias})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 343")

        if CACHE.is_in(f"{user.id}.followers"):
            CACHE._memory[CACHE._hash(f"{user.id}.followers")] = CacheItem(
                [deepcopy(followers), user.followers_soa])
        else:
            CACHE.add(key=f"{user.id}.followers", value=[
                      deepcopy(followers), user.followers_soa])
        return followers


@app.get("/{alias}/posts")
async def get_posts(alias: str,  current_user: Actor = Depends(get_current_user)):
    user=None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 363")

    if user!=None and CACHE.is_in(f"{user.id}.posts") and CACHE.get(f"{user.id}.posts")[1] == user.posts_soa:
        return CACHE.get(f"{user.id}.posts")[0]

    posts = []
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            usr_ob = node.search(user.outbox)
            with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items(["CreateActivity"]):
                    p = post_dht.search(i)
                    if p is not None:
                        dp = {}
                        dp["id"] = p.id
                        dp["author"] = p.author
                        dp["date"] = p.published
                        dp["text"] = p.content
                        dp["count_fav"] = len(p.likes)
                        dp['count_comment'] = len(p.replies)
                        dp["count_share"] = len(p.shared)
                        dp["category"] = p.cat_label
                        dp["fav"] = current_user.id in p.likes
                        dp["share"] = current_user.id in p.shared
                        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as actors_dht:
                            act = actors_dht.search(p.author)
                            if act is not None:
                                dp["username"] = act.user_name
                            else:
                                raise HTTPException(status_code=404, detail=f"Username {p.author} not found")
                        posts.append(dp)
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 378")
    if CACHE.is_in(f"{user.id}.posts"):
        CACHE._memory[CACHE._hash(f"{user.id}.posts")] = CacheItem(
            [deepcopy(posts), user.posts_soa])
    else:
        CACHE.add(key=f"{user.id}.posts", value=[
                  deepcopy(posts), user.posts_soa])

    return posts


@app.get("/me/feed")
async def get_posts(current_user: Actor = Depends(get_current_user)):
    posts = []
    try:
        with Pyro5.client.Proxy(f'PYRO:inboxes@{IP}:8002') as node:
            usr_ob = node.search(current_user.inbox)
            with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items(["CreateActivity", "ShareActivity"]):
                    p = post_dht.search(i)
                    if p is not None:
                        dp = {}
                        dp["id"] = p.id
                        dp["author"] = p.author
                        dp["date"] = p.published
                        dp["text"] = p.content
                        dp["count_fav"] = len(p.likes)
                        dp['count_comment'] = len(p.replies)
                        dp["count_share"] = len(p.shared)
                        dp["category"] = p.cat_label
                        dp["fav"] = current_user.id in p.likes
                        dp["share"] = current_user.id in p.shared
                        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as actors_dht:
                            act = actors_dht.search(p.author)
                            if act is not None:
                                dp["username"] = act.user_name
                            else:
                                raise HTTPException(status_code=404, detail=f"Username {p.author} not found")
                        posts.append(dp)
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 378")
    return posts


@app.get("/{alias}/shares")
async def get_shared(alias: str,  current_user: Actor = Depends(get_current_user)):
    user=None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
        
    except:
       raise HTTPException(
                status_code=500, detail=f"An error has occurred")
    if user!=None and CACHE.is_in(f"{user.id}.shared") and CACHE.get(f"{user.id}.shared")[1] == user.shared_soa:
        return CACHE.get(f"{user.id}.shared")[0]
    shared = []
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            usr_ob = node.search(user.outbox)

            with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items(["ShareActivity"]):
                    p = post_dht.search(i)
                    print(p)
                    if p is not None:
                        dp = {}
                        dp["id"] = p.id
                        dp["author"] = p.author
                        dp["date"] = p.published
                        dp["text"] = p.content
                        dp["count_fav"] = len(p.likes)
                        dp['count_comment'] = len(p.replies)
                        dp["count_share"] = len(p.shared)
                        dp["category"] = p.cat_label
                        dp["fav"] = current_user.id in p.likes
                        dp["share"] = current_user.id in p.shared
                        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as actors_dht:
                            act = actors_dht.search(p.author)
                            if act is not None:
                                dp["username"] = act.user_name
                            else:
                                raise HTTPException(status_code=404, detail=f"Username {p.author} not found")
                        shared.append(dp)
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 411")

    if CACHE.is_in(f"{user.id}.shared"):
        CACHE._memory[CACHE._hash(f"{user.id}.shared")] = CacheItem(
            [deepcopy(shared), user.shared_soa])
    else:
        CACHE.add(key=f"{user.id}.shared", value=[
                  deepcopy(shared), user.shared_soa])

    return shared


@app.get("/{alias}/likes")
async def get_likes(alias: str,  current_user: Actor = Depends(get_current_user)):
    user=None
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 432")


    if user!=None and CACHE.is_in(f"{user.id}.likes") and CACHE.get(f"{user.id}.likes")[1] == user.likes_soa:
        return CACHE.get(f"{user.id}.likes")[0]
    likes = []
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            usr_ob = node.search(user.outbox)

            with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as post_dht:
                for i in usr_ob.items(["LikeActivity"]):
                    p = post_dht.search(i)
                    print("LIKE", p.id)
                    if p is not None:
                        dp = {}
                        dp["id"] = p.id
                        dp["author"] = p.author
                        dp["date"] = p.published
                        dp["text"] = p.content
                        dp["count_fav"] = len(p.likes)
                        dp['count_comment'] = len(p.replies)
                        dp["count_share"] = len(p.shared)
                        dp["category"] = p.cat_label
                        dp["fav"] = current_user.id in p.likes
                        dp["share"] = current_user.id in p.shared
                        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as actors_dht:
                            act = actors_dht.search(p.author)
                            if act is not None:
                                dp["username"] = act.user_name
                            else:
                                raise HTTPException(status_code=404, detail=f"Username {p.author} not found")
                        likes.append(dp)
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"An error has occurred {e} line 448")

    if CACHE.is_in(f"{user.id}.likes"):
        CACHE._memory[CACHE._hash(f"{user.id}.likes")] = CacheItem(
            [deepcopy(likes), user.likes_soa])
    else:
        CACHE.add(key=f"{user.id}.likes", value=[
                  deepcopy(likes), user.likes_soa])

    return likes


@app.put("/me/like/{post_id}")
async def like(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(
                "LikeActivity", ("Like"+ current_user.id + post_id, current_user, post_id)
            )
            current_user.likes_soa += 1
            current_user.likes_soa %= MAX_SAVE
            
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            p = node.search(post_id)
            if p is None:
                raise HTTPException(status_code=404, detail="Post unreachable")
            p.like(current_user.id)
            p.likes_soa += 1
            p.likes_soa %= MAX_SAVE

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    
    return 'success'


@app.put("/me/share/{post_id}")
async def share_post(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            post=node.search(post_id)
            if post is None: 
                raise HTTPException(status_code=404, details="Post unreachable")
            
            post.add_shared(current_user.id)
            post.shared_soa+=1
            post.shared_soa%=MAX_SAVE

        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(
                "ShareActivity",("Share" + current_user.id +post_id, post_id))
            current_user.shared_soa+=1
            current_user.shared_soa%=MAX_SAVE

        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            try:
                with Pyro5.client.Proxy(f'PYRO:inboxes@{IP}:8002') as inb:
                    for i in current_user.followers:
                        print(i)
                        act_i = node.search(i)
                        inb.search(act_i.inbox).add("ShareActivity",("Share"+current_user.id +
                           post_id, post_id))
                        print("add")
            except:
                raise HTTPException(
                    status_code=500, detail=f"An error has occurred")
                    
    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    return 'success'


@app.delete("/me/delete_post/{post_id}")
async def delete_post(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            post = node.search(post_id)
            if post is None:
                raise HTTPException(status_code=404, detail="Post not found")

            if post.author == current_user.id:
                node.remove(post.id)
            else:
                raise HTTPException(status_code=401, detail=f"Unauthorized")

        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            outbox = node.search(current_user.outbox)
            outbox.add("DeleteActivity",('Delete'+post_id, post_id))
            current_user.posts_soa += 1
            current_user.posts_soa %= MAX_SAVE
    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    return 'success'


@app.post("/me/follow/{user_id}")
async def follow(user_id, current_user: Actor = Depends(get_current_user)):
    try:
        # Search user to follow
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user = node.search(user_id)

        try:
            # Put follow activity in your outbox
            with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as fol:
                fol.search(current_user.outbox).add(
                    "FollowActivity",('Follow'+user_id, user_id))
                user.add_followers(current_user.id)
                user.followers_soa += 1
                user.followers_soa %= MAX_SAVE
            
            current_user.add_followings(user_id)
            current_user.following_soa += 1
            current_user.following_soa %= MAX_SAVE
        except:
            raise HTTPException(
                status_code=500, detail=f"An error has occurred")

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")

    return 'success'


@app.delete("/me/unfollow/{user_id}")
async def unfollow(user_id, current_user: Actor = Depends(get_current_user)):
    current_user.remove_followings(user_id)
    current_user.following_soa += 1
    current_user.following_soa %= MAX_SAVE
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as fol:
            fol.search(current_user.outbox).add(
                "UnfollowActivity",('Unfollow'+user_id, user_id))
    except:
        raise HTTPException(
            status_code=500, detail=f"An error has occurred")
            
    try:
        with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
            user = node.search(user_id)
            user.remove_followers(current_user.id)
            user.followers_soa += 1
            user.followers_soa %= MAX_SAVE

    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
        
    return 'success'   

@app.post("/me/preferences")
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


@app.put("/me/unlike/{post_id}")
async def unlike(post_id: str, current_user: Actor = Depends(get_current_user)):
    try:
        with Pyro5.client.Proxy(f'PYRO:outboxes@{IP}:8002') as node:
            node.search(current_user.outbox).add(
                "UnlikeActivity", ("Unlike" + current_user.id + post_id, current_user, post_id)
            )

        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            p=node.search(post_id)
            if p is None:
                raise HTTPException(status_code=404, detail="Post unreachable")
            p.unlike(current_user.id)
            p.likes_soa += 1
            p.likes_soa %= MAX_SAVE

    except:
        raise HTTPException(status_code=500, detail=f"An error has occurred")
    
    
@app.get("/{alias}/info")
async def get_info(alias: str, current_user: Actor = Depends(get_current_user)):
    info={}
    with Pyro5.client.Proxy(f'PYRO:actors@{IP}:8002') as node:
        actor = node.search(alias)
        if actor is None:
            raise HTTPException(status_code=404, detail=f"Actor not found")
        else:
            info["username"]=actor.user_name
            info["alias"]=alias
            info["followers"]=len(actor.followers)
            info["following"]=len(actor.following)
            info["isFollowing"] = False
            if alias != current_user.alias and alias in current_user.following:
                info["isFollowing"] = True
    return info

@app.get("/{post_id}/get_shared_by")
async def get_shared_info(post_id:str):
    try:
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            sp = node.search(share_post)
            if sp is None:
                raise HTTPException(status_code=404, detail=f"Post not found")
            
            if sp!=None and CACHE.is_in(f"{sp.id}.shared") and CACHE.get(f"{sp.id}.shared")[1] == sp.shared_soa:
                return CACHE.get(f"{sp.id}.shared")[0]
    
            else:
                CACHE.add(key=f"{sp.id}.shared", value=[
                        deepcopy(sp.likes), sp.shared_soa])
                return sp._shared
    except:
        raise HTTPException(
                status_code=500, detail=f"An error has occurred")
        
@app.get("/{post_id}/get_likes")
async def get_likes_info(post_id:str):
    post=None
    
    try:
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            post=node.search(post_id)
            if post is None:
                raise HTTPException(status_code=404, detail=f"Post not found")
    except:
       raise HTTPException(
                status_code=500, detail=f"An error has occurred")
    
    if post!=None and CACHE.is_in(f"{post.id}.likes") and CACHE.get(f"{post.id}.likes")[1] == post.likes_soa:
        return CACHE.get(f"{post.id}.likes")[0]
    
    else:
        CACHE.add(key=f"{post.id}.likes", value=[
                  deepcopy(post.likes), post.likes_soa])
        
        return post.likes
        
@app.get("/{post_id}/get_replies")
async def get_replies_info(post_id:str):
    
    post=None
    
    try:
        with Pyro5.client.Proxy(f'PYRO:posts@{IP}:8002') as node:
            post=node.search(post_id)
            if post is None:
                raise HTTPException(status_code=404, detail=f"Post not found")
    except:
       raise HTTPException(
                status_code=500, detail=f"An error has occurred")
    
    if post!=None and CACHE.is_in(f"{post.id}.replies") and CACHE.get(f"{post.id}.replies")[1] == post.replies_soa:
        return CACHE.get(f"{post.id}.replies")[0]
    
    else:
        CACHE.add(key=f"{post.id}.replies", value=[
                  deepcopy(post.replies), post.replies_soa])
        
        return post.replies 
