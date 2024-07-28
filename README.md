# Kafka Stream Processing with Cohere and LangChain

## Overview

This project demonstrates a stream processing pipeline using Kafka for message passing, Cohere for natural language processing, and LangChain for managing prompt templates. The main objective is to extract names from a given transcript, process the names to generate summaries, and send the results back using Kafka.

## Project Structure

The project consists of two main scripts:
1. `producer.py`: Responsible for reading transcripts, extracting names using an LLM, and sending the results to a Kafka topic.
2. `consumer.py`: Responsible for consuming messages from the Kafka topic, generating summaries for each name using Cohere, and logging the results.

### `producer.py`

This script performs the following tasks:
- Reads a transcript from a Streamlit interface.
- Uses LangChain to extract names from the transcript.
- Sends the extracted names to a Kafka topic.

#### Key Functions
- `streamlit_run()`: Creates a Streamlit interface for transcript submission.
- `LLM()`: Uses LangChain and Cohere to extract names from the transcript.
- `send_to_kafka()`: Sends the extracted names to a Kafka topic asynchronously.
- `main()`: Coordinates the overall flow of reading, processing, and sending the transcript.

### `consumer.py`

This script performs the following tasks:
- Consumes messages from a Kafka topic.
- Generates summaries for each extracted name using Cohere.
- Logs the generated summaries.

#### Key Functions
- `LLMCohere()`: Generates a summary for a given name using Cohere.
- `get_summaries()`: Processes a list of names and generates summaries for each.
- `consume_messages()`: Consumes messages from a Kafka topic and processes them.

## Environment Variables

The project requires a `.env` file containing the following environment variables:
- `COHERE_API_KEY`: Your API key for the Cohere service.
- `KAFKA_BOOTSTRAP_SERVERS`: The address of your Kafka server (e.g., `localhost:9092`).

## Usage

### Running the Producer

1. Ensure Kafka is running on your local machine or server.  
2. Run `Poetry install`
3. Run the consumer script:
   ```bash
   poetry run python consumer.py
4. Run producer script:
   ```bash
   poetry run python producer.py
