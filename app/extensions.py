from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
import redis

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

def init_redis(app):
    return redis.from_url(app.config["REDIS_URL"], decode_responses=True)
