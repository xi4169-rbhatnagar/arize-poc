import dataclasses
from typing import Dict, Any, Optional

from openai import OpenAI


@dataclasses.dataclass
class Annotation:
    name: str
    label: str
    score: float
    explanation: Optional[str] = ''

    def to_payload(self, span_id: str) -> Dict[str, Any]:
        result = {"label": self.label, "score": self.score}
        if self.explanation:
            result['explanation'] = self.explanation
        return {
            "span_id": str(span_id),
            "name": self.name,
            "annotator_kind": "HUMAN",
            "result": result,
            "metadata": {},
        }


@dataclasses.dataclass
class Server:
    llm: OpenAI
