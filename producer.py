import json
from typing import List, Dict

import streamlit as st
import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
import logging

load_dotenv('.env')


class NameList(BaseModel):
    names: List[str]


def streamlit_run():
    st.title("Transcript Submission")

    st.header("Submit Your Transcript")
    transcript = st.text_area("Enter the transcript text here:", height=300)

    if st.button("Submit"):
        if transcript:
            st.success("Transcript submitted successfully!")
            st.write("Here is the transcript you submitted:")
            st.write(transcript)
            return transcript
        else:
            st.error("Please enter a transcript before submitting.")


# kafka set up
# kafka_config_producer = {
#     'bootstrap.servers': 'localhost:9092'
# }
# producer_paragraph = Producer(kafka_config_producer)
topic = 'names'
bootstrap_servers = 'localhost:9092'


def LLM(transcript: object) -> object:
    """

    :param transcript: 
    :return: 
    """
    # To AI system prompt
    SYSTEM_PROMPT_FILTERING = SystemMessagePromptTemplate.from_template(
        """
        you will be given the script and you need to extract the names of the people mentioned in the script.
        """
    )

    # Human prompt
    TRANSCRIPT_MESSAGE_FILTER = HumanMessagePromptTemplate.from_template(
        """
        script: {script}
        """
    )

    prompt = ChatPromptTemplate.from_messages([
        SYSTEM_PROMPT_FILTERING,
        TRANSCRIPT_MESSAGE_FILTER
    ])

    model = ChatOpenAI(model="gpt-4o", temperature=0)
    chain = prompt | model.with_structured_output(NameList)
    response = chain.invoke({"script": transcript})  #this gives back pydantic model nameslist
    return response


async def send_to_kafka(topic, response):
    """

    :type response: object
    :type topic: object
    """
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        json_names = response.json()  # Convert the pydantic name list to json for sending
        await producer.send_and_wait(topic, key=None, value=json_names.encode('utf-8'))
        print(f'Sent: {json_names}')
    except Exception as e:
        logging.error(f"Failed to send summary to Kafka: {e}")
    finally:
        await producer.stop()


def main():
    transcript: str = streamlit_run()
    if transcript:
        response: dict[str, BaseException | None | BaseMessage | dict | NameList] = LLM(transcript)
        asyncio.run(send_to_kafka(topic, response))


if __name__ == "__main__":
    main()
