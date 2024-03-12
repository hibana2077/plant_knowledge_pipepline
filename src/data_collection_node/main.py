'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-12 09:27:06
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from langchain_community.document_loaders import WebBaseLoader
from pprint import pprint

loader = WebBaseLoader("https://iastate.pressbooks.pub/quantitativegenetics/chapter/gene-frequencies/")
loader.requests_kwargs = {"verify":False}

data = loader.load()

pprint(data[0].page_content)