# apps/yuna/ingest.py

from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBEDDING_MODEL

def carregar_documento(caminho_pdf: str):
    loader = PyMuPDFLoader(caminho_pdf)
    return loader.load()

def indexar_documento(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    vectorstore = Qdrant.from_documents(
        documents=chunks,
        embedding=embeddings,
        location=QDRANT_HOST,
        port=QDRANT_PORT,
        collection_name=QDRANT_COLLECTION,
        force_recreate=True  # recria a coleção toda vez
    )

    print(f"✅ {len(chunks)} chunks indexados com sucesso!")

if __name__ == "__main__":
    docs = carregar_documento("data/Manual_de_Instruções_da_BDGD.pdf")
    indexar_documento(docs)
