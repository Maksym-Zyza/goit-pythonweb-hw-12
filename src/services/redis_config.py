import os
import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_client() -> redis.Redis:
    env = os.getenv("ENV", "dev")

    if env == "prod":
        return redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=False,  
        )
    else:
        return redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=False,  
        )
