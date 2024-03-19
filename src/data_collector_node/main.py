'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmaill.com
LastEditTime: 2024-03-19 14:11:34
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: Scraping data from the web
'''
import redis
import os
import logging
import time
from langchain_community.document_loaders import WebBaseLoader
from pprint import pprint
from warnings import simplefilter
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

# Connect to redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", 6379)

# client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
simplefilter(action="ignore", category=FutureWarning)
simplefilter(action="ignore", category=InsecureRequestWarning)

# loader = WebBaseLoader("https://iastate.pressbooks.pub/quantitativegenetics/")
# loader.requests_kwargs = {"verify":False}

# data = loader.load()

# print(len(data))
# pprint(data[0].page_content)

if __name__ == "__main__":
    logger.info("Data collection node active") 