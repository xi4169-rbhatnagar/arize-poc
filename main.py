import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from openai import AzureOpenAI
from opentelemetry import trace

load_dotenv('envs/deepseek.env')

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in the AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(scenario):
    with project_client:
        span = trace.get_current_span()
        span_id = span.context.span_id.to_bytes(8, 'big').hex()
        print(span_id)
        client = AzureOpenAI(
            api_key=os.environ.get('AZURE_OPENAI_KEY'),
            api_version="2024-02-01",
            azure_endpoint=os.environ.get('AZURE_OPENAI_URL')
        )

        question = "What is 2+2"
        span.set_attribute('INPUT', question)
        response = client.chat.completions.create(
            model=os.environ['MODEL_DEPLOYMENT_NAME'],  # model = "deployment_name".
            messages=[
                {"role": "user", "content": question}
            ]
        )
        output = response.choices[0].message.content
        span.set_attribute('OUTPUT', output)
