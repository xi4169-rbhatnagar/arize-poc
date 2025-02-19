import os

from fastapi import FastAPI
from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

from services import chat, feedback


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

app.include_router(chat.router.get_router(server.llm))
app.include_router(feedback.router.get_router())
