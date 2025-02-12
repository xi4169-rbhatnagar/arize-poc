import dataclasses
from typing import Dict, Any

from openai import OpenAI


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


@dataclasses.dataclass
class Server:
    llm: OpenAI
