import dataclasses

from openai import OpenAI


@dataclasses.dataclass
class Server:
    llm: OpenAI
