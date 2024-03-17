'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:30:43
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-17 19:42:40
FilePath: \plant_knowledge_pipepline\src\control_node\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from sanic import Sanic
from sanic.response import text,json

app = Sanic("MyHelloWorldApp")

@app.get("/")
async def hello_world(request):
    return json({"hello": "world"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)