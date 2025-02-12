import os
from datetime import datetime
from typing import Dict

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry import trace

from arize_utils import annotate, AnnotationReporter
from model import Server, Annotation


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


def mark_feedback(span_id: str, thumbs_up: bool):
    annotate(
        span_id,
        annotations=[
            Annotation('user-feedback', 'thumbs-up' if thumbs_up else 'thumbs-down', 1)
        ]
    )
    return "Successfully processed the annotation request"


def get_feedback_summary(start_time: datetime, end_time: datetime, project_id='UHJvamVjdDox'):
    df = AnnotationReporter.get_annotations_between(project_id, start_time, end_time)
    label_counts = df['label'].value_counts().to_dict()
    return dict(filter(lambda i: 'thumb' in i[0], label_counts.items()))
