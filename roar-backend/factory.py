from typing import Dict, Type, List
from .actor import Actor
from .post import Post
from .activities import *
from datetime import datetime
import Pyro5.server


@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class Factory:
    NAME = ""

    def produce(self, **kwargs):
        pass


@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class PostFactory(Factory):
    NAME = "post_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        author: Actor = kwargs["actor"]
        content: str = kwargs["content"]
        reply: str = kwargs["reply"]
        published: datetime = kwargs["datetime"]

        return Post(id, author, content, reply, published)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class ActorFactory(Factory):
    NAME = "actor_factory"

    def produce(self, **kwargs):
        alias: str = kwargs["alias"]
        username: str = kwargs["username"]
        hashed_password: str = kwargs["hashed_password"]

        return Actor(alias, username, hashed_password)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode="single")
class CreateActivityFactory(Factory):
    NAME = "create_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        actor: str = kwargs["actor"]
        obj: str = kwargs["obj"]
        published: datetime = kwargs["published"]
        to: List[str] = kwargs["to"]
        reply: str = kwargs["reply"]

        return CreateActivity(id, actor, obj, published, to, replay)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class DeleteActivityFactory(Factory):
    NAME = "delete_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        obj: str = kwargs["obj"]

        return DeleteActivity(id, obj) 

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class FollowActivityFactory(Factory):
    NAME = "follow_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        actor: str = kwargs["actor"]

        return FollowActivity(id, actor)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class UnfollowActivityFactory(Factory):
    NAME = "unfollow_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        actor: str = kwargs["actor"]

        return UnfollowActivity(id, actor)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class LikeActivityFactory(Factory):
    NAME = "like_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        actor: str = kwargs["actor"]
        obj: str = kwargs["obj"]

        return LikeActivity(id, actor, obj)

@Pyro5.server.expose
@Pyro5.server.behavior(instance_mode='single')
class ShareActivityFactory(Factory):
    NAME = "share_activity_factory"

    def produce(self, **kwargs):
        id: str = kwargs["id"]
        obj: str = kwargs["obj"]
        obj_share: str = kwargs["obj_share"]

        return ShareActivity(id, obj, obj_share)

FACTORY_PATH = {f.NAME: f for f in Factory.__subclasses__()}