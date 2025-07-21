# apps/yuna/chain.py

from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, OPENAI_API_KEY, OPENAI_MODEL, EMBEDDING_MODEL

def build_chain():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    qdrant = Qdrant(
        client=QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT),
        collection_name=QDRANT_COLLECTION,
        embeddings=embeddings
    )

    retriever = qdrant.as_retriever()

    llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain
