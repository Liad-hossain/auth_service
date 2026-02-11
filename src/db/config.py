import redis
from databases import Database

from src.settings import settings

# PostgreSQL Database connection
database = Database(str(settings.database_url))

# Redis connection
redis = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True,
)
