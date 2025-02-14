from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI

from models.http_params import QueryRequest, FeedbackRequest, ReportRequest

load_dotenv('../envs/deepseek.env')

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from openai import AzureOpenAI
from opentelemetry import trace

from handlers import arize

load_dotenv('envs/deepseek.env')


class Server:
    def __init__(self):
        self.project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        )

        application_insights_connection_string = self.project_client.telemetry.get_connection_string()
        if not application_insights_connection_string:
            print("Application Insights was not enabled for this project.")
            print("Enable it via the 'Tracing' tab in the AI Foundry project page.")
            exit()
        configure_azure_monitor(connection_string=application_insights_connection_string)

        self.tracer = trace.get_tracer(__name__)
        self.llm = AzureOpenAI(
            api_key=os.environ.get('AZURE_OPENAI_KEY'),
            api_version="2024-02-01",
            azure_endpoint=os.environ.get('AZURE_OPENAI_URL')
        )


app = FastAPI()
server = Server()


@app.get('/query')
def query(request: QueryRequest):
    with server.project_client:
        return arize.ask_llm_with_tracing(request.question, server.llm)


@app.post('/feedback')
def user_feedback(request: FeedbackRequest):
    raise NotImplementedError
    # return handlers.arize.mark_user_feedback(request.span_id, request.feedback)


@app.get('/report')
def get_report(request: ReportRequest):
    ist_offset = timedelta(hours=5, minutes=30)
    start_time_dt = datetime.strptime(request.start_time, '%Y-%m-%d %H:%M:%S')
    end_time_dt = datetime.strptime(request.end_time, '%Y-%m-%d %H:%M:%S')

    start_time = start_time_dt - ist_offset
    end_time = end_time_dt - ist_offset
    raise NotImplementedError
    # return handlers.arize.get_feedback_summary(start_time, end_time)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=9000)
