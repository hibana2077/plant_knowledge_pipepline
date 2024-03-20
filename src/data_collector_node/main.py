'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-20 13:33:48
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

# job structure
# {
#     "job_id": "123",
#     "job_type": "single_page", # single_page, multi_page, sitemap
#     "url": "https://iastate.pressbooks.pub/quantitativegenetics/",
#     "allowed_url_patterns": ["https://iastate.pressbooks.pub/quantitativegenetics/"],
#     "timestamp": "2024-03-03 19:29:24",
# }

if __name__ == "__main__":
    logger.info("Data collection node active")
    logger.info("Config:")
    logger.info(f"REDIS_HOST: {redis_host}")
    logger.info(f"REDIS_PORT: {redis_port}")
    while True:
        try:
            # Connect to redis
            client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
            # Check for new Jobs
            job = client.blpop("data_collection_opens_jobs", 0)
        except KeyboardInterrupt:
            logger.info("Data collection node shutting down")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            break
        except:
            logger.error("An unknown error occurred")
            break