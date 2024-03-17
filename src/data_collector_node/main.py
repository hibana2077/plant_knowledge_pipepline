'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-17 21:09:52
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: Scraping data from the web
'''
import redis
from langchain_community.document_loaders import WebBaseLoader
from pprint import pprint

loader = WebBaseLoader("https://www.ptt.cc/bbs/NBA/M.1710203659.A.06B.html")
loader.requests_kwargs = {"verify":False}

data = loader.load()

pprint(data[0].page_content)