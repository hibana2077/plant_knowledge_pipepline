'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:30:43
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-23 21:43:52
FilePath: \plant_knowledge_pipepline\src\control_node\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import redis
import os
from sanic import Sanic
from sanic.response import text,json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

app = Sanic("control_node")
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.get("/")
async def hello_world(request):
    return json({"stats": "live"})

@app.get("/get_jobs")
async def get_jobs(request):
    # get redis list without pop
    jobs = redis_client.lrange("data_collection_opens_jobs", 0, -1)
    return_list = []
    for job in jobs:
        return_list.append(job.decode("utf-8"))
    return json(return_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)