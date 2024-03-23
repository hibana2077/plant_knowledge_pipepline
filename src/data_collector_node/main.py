'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-23 20:45:47
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: Scraping data from the web
'''
import redis
import os
import logging
import time
import json
from langchain_community.document_loaders import WebBaseLoader
from pprint import pprint
from warnings import simplefilter
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

# Basic config
heartbeat_interval = os.getenv("HEARTBEAT_INTERVAL", 60)

# Connect to redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# HDFS config
HDFS_HOST = os.getenv("HDFS_HOST", "localhost")

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

def process(job_type:str, url:str, allowed_url_patterns:list):
    if job_type == "single_page":
        loader = WebBaseLoader(url)
        loader.requests_kwargs = {"verify":False}
        data = loader.load()
        print(len(data))
        pprint(data[0].page_content)
        
if __name__ == "__main__":
    logger.info("Data collection node active")
    logger.info("Config:")
    logger.info(f"REDIS_HOST: {REDIS_HOST}")
    logger.info(f"REDIS_PORT: {REDIS_PORT}")
    heartbeat_reg = time.time()
    while True:
        try:
            # Connect to redis
            client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            # Check for new Jobs
            job = client.blpop("data_collection_opens_jobs", 10)
            if job != None:
                job = json.loads(job[1].decode("utf-8"))
                logger.info(f"Received job: {job}") if time.time() - heartbeat_reg > heartbeat_interval else None
                # get job type
                job_type = job["job_type"]
                url = job["url"]
                allowed_url_patterns = job["allowed_url_patterns"]
                process(job_type, url, allowed_url_patterns)
            
        except KeyboardInterrupt:
            logger.info("Data collection node shutting down")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            break
        except:
            logger.error("An unknown error occurred")
            break