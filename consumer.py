import asyncio
import json
import os
from typing import List
import requests
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from confluent_kafka import Consumer, KafkaException, KafkaError
import logging
import httpx
import uvicorn
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from dotenv import load_dotenv
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
import cohere

logging.basicConfig(level=logging.INFO)

app = FastAPI()
load_dotenv('.env')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')


class NameList(BaseModel):
    names: List[str]


class SummaryResponse(BaseModel):
    name: str
    summary: str


kafka_bootstrap_servers = 'localhost:9092'


# kafka_config_consumer = {
#     'bootstrap.servers': 'localhost:9092',
#     'group.id': 'jkillkhj',
#     'auto.offset.reset': 'latest'
# }
#
# consumer_paragraph = Consumer(kafka_config_consumer)
# topic_out = 'names'
# consumer_paragraph.subscribe([topic_out])

# state = {"first_paragraph": None}


# @app.get("/articles/{article_name}")
# async def get_first_par(article_name: str):
#     url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{article_name}"  # from the wiki docs
#     async with httpx.AsyncClient(follow_redirects=True) as client:
#         response = await client.get(url)
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error fetching article summary.")
#     else:
#         data = response.json()
#         if "extract" in data:
#             return dict(article_name=article_name, first_paragraph=data["extract"])
#         else:
#             raise HTTPException(status_code=404, detail="Summary not available.")
#
#
# async def get_wiki(name_list: NameList):
#     for name in name_list.names:
#         try:
#             article_sum = await get_first_par(name)
#             #print(type(article_sum))
#
#             logging.info(f"Article summary for {name}: {article_sum}")
#             #await produce_messages(article_sum)
#             #print(f"Article summary for {name}: {article_sum}")
#         except HTTPException as e:
#             print(f"Error fetching article for {name}: {e.detail}")
#

def LLMCohere(name):
    cohere_model = cohere.Client(api_key=COHERE_API_KEY)
    prompt = f'Generate a summary about {name}'
    response = cohere_model.generate(
        model='command',
        prompt=prompt
    )
    #logging.info(f"Raw response from Cohere: {response.generations[0].text}")
    summary_text = response.generations[0].text.strip()
    summary_response = SummaryResponse(name=name, summary=summary_text) #convert to summary pydantic
    return summary_response


def get_summaries(names:NameList):
    summary_responses = []
    for name in names.names: #name list pydantic take the name attribute
        response = LLMCohere(name)
        if response:
            summary_responses.append(response)
    return summary_responses

async def consume_messages():
    consumer = AIOKafkaConsumer(
        'names',
        bootstrap_servers=kafka_bootstrap_servers,
        group_id='olkjjjkiiimnmnjjuuytiuyroo',
        auto_offset_reset='latest'
    )
    await consumer.start()
    try:
        logging.info("Starting the consumer...")
        async for msg in consumer:
            msg_value = msg.value.decode("utf-8")
            #logging.info(f'Received raw message: {msg_value}')
            try:
                msg_pydantic = NameList.parse_raw(msg_value)  # Convert back to pydantic
                #await get_wiki(msg_pydantic)
                logging.info(f'Parsed message: {msg_pydantic}')
                summaries = get_summaries(msg_pydantic) #sending namelist pydantic
                for summary in summaries:
                    logging.info(f'Summary for {summary.name}: {summary.summary}')
            except Exception as e:
                logging.error(f'Error parsing message: {e}')
    except asyncio.CancelledError:
        logging.info("Consumer cancelled.")
    finally:
        await consumer.stop()


#article summery gets back as a dictunatry with wiki name and summery
# async def produce_messages(article_sum):
#     producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
#     await producer.start()
#     try:
#         article_sum_json = json.dumps(article_sum)
#         await producer.send_and_wait('summary',key= None, value=article_sum_json.encode('utf-8'))
#         logging.info(f"Sent article summary to Kafka: {article_sum}")
#     except Exception as e:
#         logging.error(f"Failed to send summary to Kafka: {e}")
#     finally:
#         await producer.stop()
#


if __name__ == "__main__":
    asyncio.run(consume_messages())
