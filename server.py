import os

from dotenv import load_dotenv
from flask import Flask, request
from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

from handler import ask_llm_with_tracing
from model import Server

load_dotenv('envs/inferix.env')


def initialize_server() -> Server:
    llm = OpenAI(
        base_url=os.environ.get("OPENAI_API_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    # Start tracing OTel requests
    trace_provider = register(endpoint="http://localhost:4317")
    OpenAIInstrumentor().instrument(tracer_provider=trace_provider)
    return Server(llm)


app = Flask(__name__)
server = initialize_server()


@app.get('/query')
def query():
    question = request.json['question']
    return ask_llm_with_tracing(question, server)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
