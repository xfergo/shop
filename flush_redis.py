import redis

r = redis.Redis(host="localhost", port=6379)
r.flushall()
print("Redis успешно очищен!")