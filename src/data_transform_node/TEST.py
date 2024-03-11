'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-08 10:52:41
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-11 09:00:11
FilePath: \plant_knowledge_pipepline\src\data_transform_node\TEST.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
# chat = ChatGroq(temperature=0, groq_api_key="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", model_name="mixtral-8x7b-32768")

# system = "You are a helpful assistant."
# human = "{text}"
# prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# chain = prompt | chat
# out = chain.invoke({"text": "Explain the importance of low latency LLMs."})
# out = chat.invoke("Explain the importance of low latency LLMs.")
# print(out)



from typing import Optional

from langchain.chains import create_structured_output_runnable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

class Dog(BaseModel):
    '''Identifying information about a dog.'''

    name: str = Field(..., description="The dog's name")
    color: str = Field(..., description="The dog's color")
    fav_food: Optional[str] = Field(None, description="The dog's favorite food")

llm = ChatGroq(temperature=0, groq_api_key="", model_name="mixtral-8x7b-32768")
structured_llm = create_structured_output_runnable(Dog, llm, mode="openai-functions")
system = '''Extract information about any dogs mentioned in the user input.'''
prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "{input}"),]
)
chain = prompt | structured_llm
print(structured_llm.invoke("Harry was a chubby brown beagle who loved chicken"))
# print(chain._lc_kwargs.keys())
# print(chain._lc_kwargs['middle'][0].kwargs)
# chain._lc_kwargs['middle'][0].kwargs.pop('functions')
# chain._lc_kwargs['middle'][0].kwargs.pop('function_call')
# print("======")
# print(chain._lc_kwargs['middle'][0].kwargs)
# out = chain.invoke({"input": "Harry was a chubby brown beagle who loved chicken"})
# print(out)