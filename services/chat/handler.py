import os
from typing import Dict

from fastapi import APIRouter
from openinference.instrumentation import using_user, using_metadata
from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry import trace
from phoenix.trace import using_project

from modules.llm import ask_llm

chat_router = APIRouter(prefix="/chat", tags=["chat"])


def ask_llm_with_tracing(question: str, user_id: str, llm) -> Dict:
    tracer = trace.get_tracer(__name__)
    with using_metadata({'user_id': user_id}):
        with using_project(os.environ.get('ARIZE_PROJECT_NAME')):
            with using_user(user_id=user_id):
                with tracer.start_as_current_span("HandleFunctionCall", attributes={
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
                }) as span:
                    span_id = span.context.span_id.to_bytes(8, 'big').hex()
                    span.set_attribute(SpanAttributes.INPUT_VALUE, question)

                    # Get answer from the llm
                    response = ask_llm(question, llm, os.environ.get('MODEL_TO_USE'))

                    span.set_attribute(SpanAttributes.OUTPUT_VALUE, response)
                    return {'answer': response, 'span_id': span_id}
