import os
import json
import redis

redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))
redis_password = os.getenv('REDIS_PASSWORD')


class RedisHelper:

    def __init__(self):
        self.reis_conn = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True
        )
        self.cache_ttl = 60 * 60 * 24

    def get(self, key):
        data = self.reis_conn.get(key)
        return json.loads(data) if data is not None else None

    def set(self, key, value):
        return self.reis_conn.set(key, json.dumps(value), self.cache_ttl)

    def delete(self, key):
        return self.reis_conn.delete(key)
