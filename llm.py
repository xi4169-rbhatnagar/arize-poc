import os

from models.model import Server


def ask_llm(question: str, server: Server) -> str:
    response = server.llm.chat.completions.create(
        model=os.environ.get('MODEL_TO_USE'),
        messages=[
            {"role": "user", "content": question}
        ],
    )
    return response.choices[0].message.content
