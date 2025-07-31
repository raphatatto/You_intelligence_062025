# apps/yuna/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Chave da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Qdrant local
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Nome da coleção vetorial
QDRANT_COLLECTION = "documentos-yuna"

# Modelo de embedding
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Modelo de LLM
OPENAI_MODEL = "gpt-3.5-turbo"
