import json
from typing import List, Dict

import streamlit as st
import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from langchain_core.messages import BaseMessage
from cohere import Client as CohereClient
import cohere
from pydantic import BaseModel
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
import logging
import cohere
from langchain_cohere import ChatCohere

load_dotenv('.env')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')


transcript = "Bill Gates."

class NameList(BaseModel):
    names: List[str]
    cho: str


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


topic = 'names'
bootstrap_servers = 'localhost:9092'


def LLM(transcript: object) -> object:
    """

    :param transcript: 
    :return: 
    """
    SYSTEM_PROMPT_FILTERING = SystemMessagePromptTemplate.from_template(
        """
        You will be given the script and you need to extract the names of the people mentioned in the script. return only the list of names nothing else.
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

    model = ChatCohere()
    chain = prompt | model.with_structured_output(NameList)
    response = chain.invoke({"script": transcript})  # this gives back pydantic model nameslist
    #print(response)
    return response


async def send_to_kafka(topic, response, cho):
    """

    :type response: object
    :type topic: object
    """
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        value = response.json()  # Convert the pydantic name list to json for sending
        await producer.send_and_wait(topic, key=None, value=json.dumps(value).encode('utf-8'))
        print(f'Sent: {value}')
    except Exception as e:
        logging.error(f"Failed to send summary to Kafka: {e}")
    finally:
        await producer.stop()


def main():
    # transcript: str = streamlit_run()
    # if transcript:
    cho = "one sentence"
    response = LLM(transcript)  #response has the pyndatic model namelist which also contains choice
    response.cho = cho
    asyncio.run(send_to_kafka(topic, response, cho))


if __name__ == "__main__":
    main()
