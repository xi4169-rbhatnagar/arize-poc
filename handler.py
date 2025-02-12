import os
from typing import Dict

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry import trace

from model import Server


def ask_llm(question: str, server: Server) -> str:
    response = server.llm.chat.completions.create(
        model=os.environ.get('MODEL_TO_USE'),
        messages=[
            {"role": "user", "content": question}
        ],
    )
    return response.choices[0].message.content


def ask_llm_with_tracing(question, server) -> Dict:
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("HandleFunctionCall", attributes={
        SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
    }) as span:
        span_id = span.context.span_id.to_bytes(8, 'big').hex()
        span.set_input(question)

        # Get answer from the llm
        response = ask_llm(question, server)

        span.set_output(response)
        return {'answer': response, 'span_id': span_id}
