import streamlit as st
from src.agent import criar_agente
from src.rag.policy_retriever import get_policy_retriever
from src.tools.database import init_db

st.set_page_config(
    page_title="HarmonIA — Empório da Música",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 HarmonIA")
st.subheader("Assistente Virtual da Empório da Música")
st.markdown("---")

# Pré-carrega o banco SQLite em memória e a base RAG para eliminar latência na 1ª consulta
if "warmed_up" not in st.session_state:
    with st.spinner("Inicializando sistemas..."):
        init_db()
        get_policy_retriever()
        st.session_state.warmed_up = True

# Mantém a mesma instância do agente na sessão do navegador
if "agent" not in st.session_state:
    st.session_state.agent = criar_agente(verbose=False)

# Inicializa o histórico de conversas
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá! Sou o HarmonIA, assistente da Empório da Música. Como posso te ajudar com produtos, pedidos ou políticas da loja?"
        }
    ]

# Renderiza o histórico na tela
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Captura a entrada do cliente
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Executa o agente ReAct e exibe a resposta
    with st.chat_message("assistant"):
        with st.spinner("Consultando sistemas..."):
            try:
                resposta = st.session_state.agent.invoke({"input": prompt})
                output = resposta.get("output", "Não foi possível gerar uma resposta.")
            except Exception as e:
                output = f"Ocorreu um erro durante a consulta: {str(e)}"

            st.write(output)
            st.session_state.messages.append({"role": "assistant", "content": output})