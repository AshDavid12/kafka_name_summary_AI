import json
from typing import List

import streamlit as st
import asyncio
#from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

os.environ["OPENAI_API_KEY"] = "bla"

transcript = '''
Barak Obama is ok. Donald Trump is crazy.

'''


####this will be sending names identified by AI to kafka


class NameList(BaseModel):
    names: List[str]


# kafka set up
kafka_config_producer = {
    'bootstrap.servers': 'localhost:9092'
}
producer_paragraph = Producer(kafka_config_producer)
topic = 'names'

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


#print(f'{response}')

def send_to_kafka(producer, topic,response):
    #for name in response:
        #json_names = json.dumps({"list":name})  # serializtion for each pydantic paragraph model to json for kafka
    json_names = response.json() ##just convert the pydantic name list to json for sending
    producer.produce(topic, key=None, value=json_names.encode('utf-8'))
    producer.flush()
    print(f'Sent: {json_names}')


#
#
# def delivery_report(err, msg):
#     if err is not None:
#         print(f'Message delivery failed: {err}')
#     else:
#         print(f'Message delivered to {msg.topic()} [{msg.partition()}] key: {msg.key()}, value: {msg.value()}')
#         #the value is in byte format so the value will have a b and then the json string
#
#
# producer_paragraph.flush()
#
#
def main():
    send_to_kafka(producer_paragraph, topic,response)
    # st.title("Transcript Submission")

    # st.header("Submit Your Transcript")
    # transcript = st.text_area("Enter the transcript text here:", height=300)

    # if st.button("Submit"):
    #     if transcript:
    #         st.success("Transcript submitted successfully!")
    #         st.write("Here is the transcript you submitted:")
    #         st.write(transcript)
    #         serialized_paragraphs = pydantic_paragraphs(transcript)
    #         send_to_kafka(producer_paragraph,topic,serialized_paragraphs)
    #     else:
    #         st.error("Please enter a transcript before submitting.")


if __name__ == "__main__":
    main()
