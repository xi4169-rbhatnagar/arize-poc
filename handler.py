from datetime import datetime
from typing import Dict

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from opentelemetry import trace

from arize_utils import AnnotationHelper
from llm import ask_llm
from models.model import Annotation


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


def mark_user_feedback(span_id: str, feedback: str):
    AnnotationHelper.annotate(
        span_id,
        annotations=[
            Annotation('user-feedback', feedback, 1)
        ]
    )
    return "Successfully processed the annotation request"


def get_feedback_summary(start_time: datetime, end_time: datetime, project_id='UHJvamVjdDox'):
    df = AnnotationHelper.get_annotations_between(project_id, start_time, end_time)
    label_counts = df['label'].value_counts().to_dict()
    return dict(filter(lambda i: 'thumb' in i[0], label_counts.items()))
