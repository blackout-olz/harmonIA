from typing import Optional, List

try:
    from langchain.agents import AgentExecutor
except ImportError:
    try:
        from langchain.agents.agent_executor import AgentExecutor
    except ImportError:
        from langchain_classic.agents import AgentExecutor

try:
    from langchain.agents import create_tool_calling_agent
except ImportError:
    try:
        from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
    except ImportError:
        from langchain_classic.agents import create_tool_calling_agent

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config import get_llm
from src.tools.data_tools import buscar_produtos, consultar_status_pedido
from src.rag.policy_retriever import consultar_politicas
from src.agent.prompts import SYSTEM_PROMPT


def criar_agente(verbose: bool = True) -> AgentExecutor:
    """
    Instancia o LLM via Factory, vincula as ferramentas e constrói o AgentExecutor.
    """
    llm = get_llm()
    tools = [buscar_produtos, consultar_status_pedido, consultar_politicas]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)