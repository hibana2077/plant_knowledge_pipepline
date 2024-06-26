'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmaill.com
LastEditTime: 2024-04-29 11:42:44
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: Scraping data from the web
'''
import redis
import requests
import os
import logging
import time
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as parquet
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import RecursiveUrlLoader
from warnings import simplefilter
from urllib3.exceptions import InsecureRequestWarning
from typing import Optional

# Basic config
heartbeat_interval = os.getenv("HEARTBEAT_INTERVAL", 60)

# Connect to redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# HDFS config
HDFS_HOST = os.getenv("HDFS_HOST", "localhost")
HDFS_PORT = os.getenv("HDFS_PORT", 9870)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
simplefilter(action="ignore", category=FutureWarning)
simplefilter(action="ignore", category=InsecureRequestWarning)

# job structure
# {
#     "job_id": "123",
#     "job_type": "single_page", # single_page, multi_page, sitemap
#     "url": "https://iastate.pressbooks.pub/quantitativegenetics/", # url or list of urls
#     "timestamp": "2024-03-03 19:29:24",
# }

def process(job_type:str, url:str, prefix:Optional[str]) -> pd.DataFrame:
    if job_type == "single_page":
        query_url = f"https://r.jina.ai/{url}"
        r = requests.get(query_url)
        if r.status_code != 200:
            raise Exception(f"Failed to fetch data from {query_url}")
        df = pd.DataFrame({'content':r.text, 'url':url}, index=[0])
        return df
    
    elif job_type == "multi_page":
        multi_pages_loader = RecursiveUrlLoader(url)
        multi_pages = multi_pages_loader.load()
        multi_pages = [page.metadata['source'] for page in multi_pages if page.metadata['source'].startswith(prefix)]
        data = []
        for page in multi_pages:
            query_url = f"https://r.jina.ai/{page}"
            r = requests.get(query_url)
            if r.status_code != 200:
                raise Exception(f"Failed to fetch data from {query_url}")
            data.append({'content':r.text, 'url':page})
        df = pd.DataFrame(data)
        return df
        
if __name__ == "__main__":
    logger.info("Data collection node active")
    logger.info("Config:")
    logger.info(f"REDIS_HOST: {REDIS_HOST}")
    logger.info(f"REDIS_PORT: {REDIS_PORT}")
    logger.info(f"HEARTBEAT_INTERVAL: {heartbeat_interval}")
    logger.info(f"HDFS_HOST: {HDFS_HOST}")
    logger.info(f"HDFS_PORT: {HDFS_PORT}")
    fs_client = pa.hdfs.connect(HDFS_HOST, HDFS_PORT)
    # Creat directory if not exists (HDFS)
    fs_client.create_dir("/data/textract")
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
                df = process(job_type, url)
                # Save data to HDFS
                file_name = f"/data/textract/{job['job_id']}.parquet"
                with fs_client.open(file_name, 'wb') as f:
                    parquet.write_table(pa.Table.from_pandas(df), f)
                # Save metadata to redis
                client.hset("data_collection_metadata", job["job_id"], json.dumps({"file_name":file_name}))
                logger.info(f"Job {job['job_id']} completed")
                # Send heartbeat
                heartbeat_reg = time.time() if time.time() - heartbeat_reg > heartbeat_interval else heartbeat_reg
            else:
                logger.info("No jobs available")
        except KeyboardInterrupt:
            logger.info("Data collection node shutting down")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            break
        except:
            logger.error("An unknown error occurred")
            break