from src.agent.core import criar_agente

def executar_agente(pergunta: str) -> str:
    """
    Função utilitária de entrada para processar perguntas do usuário.
    """
    agente = criar_agente(verbose=False)
    resposta = agente.invoke({"input": pergunta})
    return resposta.get("output", "Não foi possível processar a resposta.")