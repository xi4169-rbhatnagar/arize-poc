import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, request
from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

import handler
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

    return Server(llm=llm)


app = Flask(__name__)
server = initialize_server()


@app.get('/query')
def query():
    question = request.json['question']
    return handler.ask_llm_with_tracing(question, server)


@app.post('/feedback')
def user_feedback():
    span_id = request.json['span_id']
    thumbs_up = request.json['thumbs_up']
    return handler.mark_feedback(span_id, thumbs_up)


@app.get('/report')
def get_report():
    ist_offset = timedelta(hours=5, minutes=30)
    start_time_str = request.json['start_time']
    end_time_str = request.json['end_time']

    start_time_dt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time_dt = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    start_time = start_time_dt - ist_offset
    end_time = end_time_dt - ist_offset
    return handler.get_feedback_summary(start_time, end_time)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
