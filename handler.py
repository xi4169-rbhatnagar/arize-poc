import os
from typing import Dict

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry import trace


def ask_llm_with_tracing(question, server) -> Dict:
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("HandleFunctionCall", attributes={
        SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
    }) as span:
        span_id = span.context.span_id.to_bytes(8, 'big').hex()
        completion = server.llm.chat.completions.create(
            model=os.environ.get('MODEL_TO_USE'),
            messages=[
                {"role": "user", "content": question}
            ],
        )
        output = completion.choices[0].message.content
        span.set_input(question)
        span.set_output(output)
        return {'answer': output, 'span_id': span_id}
