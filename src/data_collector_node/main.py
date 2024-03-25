'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-03-03 19:29:24
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-03-25 08:56:38
FilePath: \plant_knowledge_pipepline\src\data_collection_node\main.py
Description: Scraping data from the web
'''
import redis
import os
import logging
import time
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as parquet
from langchain_community.document_loaders import WebBaseLoader
from warnings import simplefilter
from urllib3.exceptions import InsecureRequestWarning

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

def process(job_type:str, url:str|list) -> pd.DataFrame:
    if job_type == "single_page":
        loader = WebBaseLoader(url)
        loader.requests_kwargs = {"verify":False}
        data = loader.load()
        cleaned_list = list()
        for idx in range(1, len(data[0].page_content)):
            if data[0].page_content[idx] != '\n' and data[0].page_content[idx-1] != '\n':
                cleaned_list.append(data[0].page_content[idx])
            elif data[0].page_content[idx] != '\n' and data[0].page_content[idx-1] == '\n':
                cleaned_list.append('\n')
                cleaned_list.append(data[0].page_content[idx])
        cleaned_list = "".join(cleaned_list).split("\n")
        df = pd.DataFrame({'content':cleaned_list})
        return df
    
    elif job_type == "multi_page":
        loader = WebBaseLoader(url)
        loader.requests_kwargs = {"verify":False}
        data = loader.load()
        cleaned_list = list()
        for data_idx in range(len(data)):
            for idx in range(1, len(data[data_idx].page_content)):
                if data[0].page_content[idx] != '\n' and data[data_idx].page_content[idx-1] != '\n':
                    cleaned_list.append(data[data_idx].page_content[idx])
                elif data[0].page_content[idx] != '\n' and data[data_idx].page_content[idx-1] == '\n':
                    cleaned_list.append('\n')
                    cleaned_list.append(data[data_idx].page_content[idx])
        cleaned_list = "".join(cleaned_list).split("\n")
        df = pd.DataFrame({'content':cleaned_list})
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