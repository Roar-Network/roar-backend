from datetime import datetime
from email import message
from os import stat
from re import S
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
import Pyro5.client
from actor import Actor
from activities import*
from post import Post

class User:
    def __init__(self, name,alias,password):
        self.username=name
        self.alias=alias
        self.password=password
    

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

@app.get("/collection")
def collection(doc_id: int):
    a = [User("Ariel", "ariel.119"), User("B", "ss")]
    try:
        return a[doc_id]
    except:
        raise HTTPException(status_code=404, detail="User id not found")
       
@app.put("/crate_user")
def create_user(username:str,alias:str,password:str):
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            if node.search(alias) is None:
                node.add(Actor(alias,user_name=username))
                
            else: raise HTTPException(status_code=400, detail=f"User {alias} already exist")
  
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
       
@app.post("/log_user")
def log_user(alias:str,password:str):
    #Contraseña incorrecta
    #raise HTTPException(status_code=401, detail=f"Wrong password for user{data[0]}")

    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            if node.search(alias) is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else: 
                #Se loggea
                pass
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
           
@app.post("/{alias}/change_password")
def change_password(alias,password:str):
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else: 
                #Cambia la contraseña
                #user.password=password 
                pass
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
@app.post("/{alias}/post") 
def create_post(alias,post):
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else: 
                #Revisar si el usuario está loggeado Error 401
                #Subir post
                try:
                    ca=CreateActiity(post.id+post.published,alias,"Post",post.published,user.followers)
                    with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
                        node.search(user.outbox).add(ca)
                    
                    for i in user.followers: 
                        with Pyro5.client.Proxy('PYRO:inboxes@172.28.5.1:8002') as node:
                            node.search(i.intbox).add(ca)
                        
                except:
                    raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
@app.get("/{alias}/following")
def get_following(alias):
    #Revisar si el usuario está loggeado Error 401
    #Revisar si el usuario existe
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else:
                following={}
                for i in user.following:
                    try:
                        usr=node.search(i)
                        if usr is None: raise HTTPException(status_code=404, detail=f"Username {i} not found")
                         
                        else:   
                            following[i]=usr
                            
                    except:
                        raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
@app.get("/{alias}/followers")
def get_followers(alias):
    #Revisar si el usuario está loggeado Error 401
    #Revisar si el usuario existe
    #si está autenticado devolver followers
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else:
                followers={}
                for i in user.followers:
                    try:
                        usr=node.search(i)
                        if usr is None: raise HTTPException(status_code=404, detail=f"Username {i} not found")
                         
                        else:   
                            followers[i]=usr
                            
                    except:
                        raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")

@app.get("/{alias}/posts")
def get_posts(alias):
    #Revisar si el usuario está loggeado Error 401
    #Revisar si el usuario existe
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else:
                posts=[]
                try:
                
                    try:
                        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
                            usr_ob=node.search(user.outbox)
                            for i in usr_ob.items:
                                if i.type=="CreateActiity":
                                    if i.obj.type=="Post":
                                        posts.append(i)
                                
                            
                    except:
                        raise HTTPException(status_code=500,detail=f"An error has occurred")
                except:
                    raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    
@app.get("/{alias}/likes")
def get_posts(alias):
    #Revisar si el usuario está loggeado Error 401
    #Revisar si el usuario existe
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else:
                likes=[]
                try:
                
                    try:
                        with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
                            usr_ob=node.search(user.outbox)
                            for i in usr_ob.items:
                                if i.type=="Like":
                                    likes.append(i)
                                
                            
                    except:
                        raise HTTPException(status_code=500,detail=f"An error has occurred")
                except:
                    raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
  
@app.put("/{alias}/like") 
def like(alias,post):
    try:
        with Pyro5.client.Proxy('PYRO:actors@172.28.5.1:8002') as node:
            user=node.search(alias)
            if user is None:
                raise HTTPException(status_code=404, detail=f"Username {alias} not found")
                
            else: 
                #Revisar si el usuario está loggeado Error 401
                #Subir post
                try:
                    ca=LikeActivity("Like",user,post)
                    with Pyro5.client.Proxy('PYRO:outboxes@172.28.5.1:8002') as node:
                        p=node.search(user.outbox).search(post)
                        p.like(user)
                        
                except:
                    raise HTTPException(status_code=500,detail=f"An error has occurred")
            
    except:
        raise HTTPException(status_code=500,detail=f"An error has occurred")
    

     
    

    
