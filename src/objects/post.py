from RObjects import RObject
from actor import Actor
import datetime 

class Post(RObject):
    def __init__(self,id,author:Actor,content:str):
        super().__init__(id,"Post")
        self.author=author
        self.content=content
        self.published=datetime.now()
        self.likes={}
        
    def like(self,alias:str):
        self.likes[alias]=alias
        
   
        
        

    