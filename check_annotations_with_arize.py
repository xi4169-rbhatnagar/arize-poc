import dataclasses
import os
import random
from typing import List, Dict, Any, Tuple

import httpx
from dotenv import load_dotenv
from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry import trace
from phoenix.otel import register

load_dotenv()


@dataclasses.dataclass
class Annotation:
    name: str
    label: str
    score: float

    def to_payload(self, span_id: str) -> Dict[str, Any]:
        return {
            "span_id": str(span_id),
            "name": self.name,
            "annotator_kind": "HUMAN",
            "result": {"label": self.label, "score": self.score},
            "metadata": {},
        }


def annotate(span_id: str, annotations: List[Annotation]):
    hclient = httpx.Client()

    annotation_payload = {
        "data": [*map(lambda a: a.to_payload(span_id), annotations)],
    }

    hclient.post(
        os.environ.get('ARIZE_URL') + "/span_annotations?sync=false",
        json=annotation_payload,
    )


# Start tracing OTel requests
trace_provider = register(endpoint="http://localhost:4317")
OpenAIInstrumentor().instrument(tracer_provider=trace_provider)

# query an llm
client = OpenAI(
    base_url=os.environ.get("OPENAI_API_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
tracer = trace.get_tracer(__name__)
x, y = (random.randint(0, 50) for _ in range(2))
span_id_and_feedbacks: List[Tuple[str, List[Annotation]]] = []
for _ in range(5):
    with tracer.start_as_current_span("HandleFunctionCall", attributes={
        SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
    }) as span:
        span_id = span.context.span_id.to_bytes(8, 'big').hex()
        question = f"What is {x}+{y}?"
        completion = client.chat.completions.create(
            model=os.environ.get('MODEL_TO_USE'),
            messages=[
                {"role": "user", "content": question}
            ],
        )
        output = completion.choices[0].message.content
        span.set_input(question)
        span.set_output(output)

        span_id_and_feedbacks.append((span_id, [
            Annotation('user-feedback', 'thumbs-up' if str(x + y) in output else 'thumbs-down', 1),
            Annotation('metrics', 'char-count', len(output))
        ]))

for span_id, annotations in span_id_and_feedbacks:
    annotate(span_id, annotations)
