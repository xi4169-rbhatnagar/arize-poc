import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

from handlers.chat import ask_llm_with_tracing
from handlers.feedback import mark_user_feedback, get_feedback_summary
from models.http_params import QueryRequest, FeedbackRequest, ReportRequest

load_dotenv('../envs/deepseek.env')


class Server:
    def __init__(self, llm: OpenAI):
        self.llm = llm


def initialize_server() -> Server:
    llm = OpenAI(
        base_url=os.environ.get("OPENAI_API_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Start tracing OTel requests
    trace_provider = register(endpoint="http://localhost:4317")
    OpenAIInstrumentor().instrument(tracer_provider=trace_provider)

    return Server(llm=llm)


app = FastAPI()
server = initialize_server()


@app.get('/query')
def query(request: QueryRequest):
    return ask_llm_with_tracing(request.question, server.llm)


@app.post('/feedback')
def user_feedback(request: FeedbackRequest):
    return mark_user_feedback(request.span_id, request.feedback)


@app.get('/report')
def get_report(request: ReportRequest):
    ist_offset = timedelta(hours=5, minutes=30)
    start_time_dt = datetime.strptime(request.start_time, '%Y-%m-%d %H:%M:%S')
    end_time_dt = datetime.strptime(request.end_time, '%Y-%m-%d %H:%M:%S')

    start_time = start_time_dt - ist_offset
    end_time = end_time_dt - ist_offset
    return get_feedback_summary(start_time, end_time)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=7000)
