<!--
 * @Author: hibana2077 hibana2077@gmaill.com
 * @Date: 2024-03-26 07:05:15
 * @LastEditors: hibana2077 hibana2077@gmaill.com
 * @LastEditTime: 2024-03-26 09:23:26
 * @FilePath: /plant_knowledge_pipepline/docs/api_docs.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# API func

## POST

### /api/v1/chat

與機器人對話

#### Request

```json
{
    "message": "Hello",
    "ai_model": "gpt2"
}
```

#### Response

```json
{
    "message": "Hi",
    "ai_model": "gpt2"
}
```

### /api/v1/history

查看對話歷史

#### Request

```json
{
    "user_id": "123456",
    "chat_id": "123456"
}
```

#### Response

```json
{
    "conversation": [
        {
            "message": "Hello",
            "from": "user"
        },
        {
            "message": "Hi",
            "from": "bot"
        }
    ]
}
```