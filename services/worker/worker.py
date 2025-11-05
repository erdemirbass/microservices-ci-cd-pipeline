import os
import time

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def main():
    while True:
        job = client.lpop("jobs")
        if job is not None:
            print(f"Processed job: {job}")
            time.sleep(0.2)
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
