import os

from flask import Flask
from redis import Redis

app = Flask(__name__)
redis_host = os.getenv("HOST") or "localhost"
redis_port = int(os.getenv("PORT") or "6379")
redisDb = Redis(host=redis_host, port=redis_port)

@app.route("/")

def welcome():
    visitCount = redisDb.incr('visitCount')
    visitCount += 1
    return f"Welcome to the Python Installer App! You have visited {visitCount} times."

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = True)
