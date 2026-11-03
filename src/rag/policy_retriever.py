import os
import json
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

# Diretorio base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def localiza_pdf_politicas() -> Path:
    """Localiza o arquivo PDF de politicas na pasta data/."""
    candidatos = [
        DATA_DIR / "políticas_da_loja.pdf",
    ]
    for c in candidatos:
        if c.exists():
            return c

    # Fallback: busca qualquer arquivo .pdf na pasta data/
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    raise FileNotFoundError(f"Nenhum arquivo PDF encontrado na pasta: {DATA_DIR}")

_retriever_instance = None

def get_policy_retriever():
    """
    Inicializa (ou retorna a instancia existente) do sistema de busca vetorial FAISS.
    Le o PDF de politicas, divide em trechos e cria os embeddings locais.
    """
    global _retriever_instance
    if _retriever_instance is not None:
        return _retriever_instance

    pdf_path = localiza_pdf_politicas()

    # 1. Carregamento do PDF
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    # 2. Fragmentacao em Chunks (500 caracteres por bloco com 50 de sobreposicao)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Embeddings locais e Vetorizacao FAISS em memoria
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_documents(chunks, embeddings)

    # 4. Configura o recuperador para trazer os 3 trechos mais relevantes
    _retriever_instance = vector_store.as_retriever(search_kwargs={"k": 3})
    return _retriever_instance


@tool
def consultar_politicas(duvida: str) -> str:
    """
    Consulta o documento oficial de politicas da Emporio da Musica para responder duvidas sobre:
    prazos de entrega, garantia, procedimentos de troca e devolucao, formas de pagamento e regras gerais.

    Args:
        duvida: A pergunta ou palavra-chave referente às regras da loja (ex: 'como funciona a devolucao?', 'qual a garantia de violoes?').
    """
    try:
        retriever = get_policy_retriever()
        docs = retriever.invoke(duvida)

        if not docs:
            return json.dumps({
                "mensagem": "Nenhuma politica especifica encontrada para este termo."
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
            "erro": f"Falha ao consultar politicas da loja: {str(e)}"
        }, ensure_ascii=False)