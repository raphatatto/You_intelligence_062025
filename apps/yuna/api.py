# apps/yuna/api.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from chain import build_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YUNA – Assistente You.On")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    pergunta: str

qa_chain = build_chain()

@app.post("/chat")
def responder(input: ChatInput):
    resposta = qa_chain(input.pergunta)
    return {
        "resposta": resposta["result"]
    }
