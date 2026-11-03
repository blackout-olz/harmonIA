import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_PATH = DATA_DIR / "faiss_index"
MODEL_PATH = DATA_DIR / "models" / "all-MiniLM-L6-v2"

_retriever_instance = None
_embeddings_instance = None


def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        if MODEL_PATH.exists():
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name=str(MODEL_PATH),
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
    return _embeddings_instance


def get_policy_retriever():
    global _retriever_instance
    if _retriever_instance is not None:
        return _retriever_instance

    embeddings = get_embeddings()

    if INDEX_PATH.exists():
        vector_store = FAISS.load_local(
            str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True
        )
    else:
        pdf_path = DATA_DIR / "políticas_da_loja.pdf"
        if not pdf_path.exists():
            pdf_path = DATA_DIR / "politicas_da_loja.pdf"

        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        # Chunk de 1200 garante que a tabela de horários inteira fica no mesmo bloco
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(str(INDEX_PATH))

    # k=6 garante recuperação completa em perguntas compostas (ex: endereço + horário)
    _retriever_instance = vector_store.as_retriever(search_kwargs={"k": 6})
    return _retriever_instance


@tool
def consultar_politicas(duvida: str) -> str:
    """Consulta o manual interno e documento de políticas da Empório da Música.

    Use esta ferramenta para responder a dúvidas sobre:
    - Endereço físico, localização e canais de contacto.
    - Horário de funcionamento presencial e no WhatsApp (dias da semana e sábados).
    - Regras de frete, prazos de entrega e entregas em Campo Grande.
    - Políticas de trocas, devoluções e direito de arrependimento.
    - Formas de pagamento, regras de parcelamento e desconto no PIX.
    - Garantia legal e do fabricante.

    Args:
        duvida: A pergunta ou palavra-chave sobre as políticas/regras da loja.
    """
    retriever = get_policy_retriever()
    docs = retriever.invoke(duvida)
    if not docs:
        return "Nenhuma informação relevante encontrada no manual de políticas."

    return "\n\n---\n\n".join([doc.page_content for doc in docs])