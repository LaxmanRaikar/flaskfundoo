import redis


r = redis.StrictRedis(host='localhost', port=6379, db=0)


"""This class is used to set , get  from Redis cache"""


class redis_methods:

    def set_method(self, key, value):
        print(value)
        r.set(key, value)       # this method is used to  add the data to redis
      

    def get_method(self, key):
        token = r.get(key)       # this method is used to  get the data out of redis
        return token

    def flush(self):             # this method is used to delete data from redis
        r.flushall()