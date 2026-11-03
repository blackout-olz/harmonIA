import os
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

load_dotenv()

def get_llm() -> BaseChatModel:
    """
    Retorna a instância do modelo LLM baseada na variável LLM_PROVIDER do .env.
    Suporta: groq, gemini, openai e ollama.
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        # Permite configurar o modelo no .env (padrão: llama-3.3-70b-versatile)
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada no arquivo .env.")
        return ChatGroq(
            model=model,
            temperature=0,
            api_key=api_key
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env.")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=api_key
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env.")
        return ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key
        )

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        return ChatOllama(
            base_url=base_url,
            model=model_name,
            temperature=0
        )

    else:
        raise ValueError(
            f"Provedor '{provider}' não suportado. "
            "Opções válidas no .env: 'groq', 'gemini', 'openai' ou 'ollama'."
        )

if __name__ == "__main__":
    try:
        llm = get_llm()
        resposta = llm.invoke("Responda em uma frase: O que é a Empório da Música?")
        print(f"[{os.getenv('LLM_PROVIDER')}] Teste concluído com sucesso:")
        print(resposta.content)
    except Exception as e:
        print("Erro ao testar a LLM:", e)