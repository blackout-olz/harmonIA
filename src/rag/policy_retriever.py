import os
import json
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_PATH = DATA_DIR / "faiss_index"

# Desativa chamadas de telemetria e verificações remotas lentas do Hugging Face Hub
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def localiza_pdf_politicas() -> Path:
    candidatos = [
        DATA_DIR / "políticas_da_loja.pdf",
        DATA_DIR / "politicas_da_loja.pdf",
        DATA_DIR / "politicas_loja.pdf",
    ]
    for c in candidatos:
        if c.exists():
            return c

    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    raise FileNotFoundError(f"Nenhum arquivo PDF encontrado na pasta: {DATA_DIR}")

_retriever_instance = None
_embeddings_instance = None

def get_embeddings():
    """Instancia o modelo de embeddings reaproveitando a mesma memoria."""
    global _embeddings_instance
    if _embeddings_instance is None:
        # local_files_only=True impede o download/checagem HTTP na HuggingFace a cada execução
        try:
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu", "local_files_only": True}
            )
        except Exception:
            # Fallback para o primeiro download caso ainda não esteja em cache local
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
    return _embeddings_instance


def get_policy_retriever():
    global _retriever_instance
    if _retriever_instance is not None:
        return _retriever_instance

    embeddings = get_embeddings()

    if INDEX_PATH.exists():
        vector_store = FAISS.load_local(
            str(INDEX_PATH), 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        pdf_path = localiza_pdf_politicas()
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(str(INDEX_PATH))

    _retriever_instance = vector_store.as_retriever(search_kwargs={"k": 3})
    return _retriever_instance


@tool
def consultar_politicas(duvida: str) -> str:
    """
    Consulta o documento oficial de políticas da Empório da Música para responder dúvidas sobre:
    prazos de entrega, garantia, procedimentos de troca e devolução, formas de pagamento e regras gerais.

    Args:
        duvida: A pergunta ou palavra-chave referente às regras da loja.
    """
    try:
        retriever = get_policy_retriever()
        docs = retriever.invoke(duvida)

        if not docs:
            return json.dumps({
                "mensagem": "Nenhuma política específica encontrada para este termo."
            }, ensure_ascii=False)

        trechos = [
            {"trecho": doc.page_content, "pagina": doc.metadata.get("page", 1) + 1}
            for doc in docs
        ]

        return json.dumps({
            "duvida": duvida,
            "trechos_encontrados": trechos
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "erro": f"Falha ao consultar políticas da loja: {str(e)}"
        }, ensure_ascii=False)