# Transcript to Kafka Pipeline

This project provides a pipeline for submitting a transcript through a Streamlit web interface, processing it using an LLM (Language Model), extracting names from the transcript, and sending the results to a Kafka topic. Additionally, it includes a consumer service that processes the Kafka messages, fetches Wikipedia summaries for the extracted names, and sends these summaries to another Kafka topic.

## Files

- `producer.py`: Contains the Streamlit app and Kafka producer logic. It submits transcripts, processes them using an LLM to extract names, and sends the results to a Kafka topic.
- `consumer.py`: Contains the FastAPI app and Kafka consumer logic. It consumes messages from the Kafka topic, fetches Wikipedia summaries for the extracted names, and sends these summaries to another Kafka topic.

## Usage
This service runs a Streamlit app where users can submit transcripts.
`streamlit run producer.py`

Run consumer:`poetry run python consumer.py`

- branch cohere_ai has a version if this code with modification to use cohere instead of OPENAI and other features.
