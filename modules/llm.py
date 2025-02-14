import os

from models.model import Server


def ask_llm(question: str, llm_client, model) -> str:
    response = llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": question}
        ],
    )
    return response.choices[0].message.content
