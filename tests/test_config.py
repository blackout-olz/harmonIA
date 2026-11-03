import pytest
import os
from unittest.mock import patch
from langchain_core.language_models import BaseChatModel
from src.config import get_llm

def test_get_llm_provedor_invalido():
    """Garante que um provedor desconhecido lança um ValueError claro."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "provedor_inexistente"}):
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        assert "Provedor 'provedor_inexistente' não suportado" in str(exc_info.value)

def test_get_llm_instanciacao_groq():
    """Garante que a factory instancia um objeto LLM válido para o Groq."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "groq", "GROQ_API_KEY": "gsk_chave_falsa_apenas_para_teste"}):
        llm = get_llm()
        assert isinstance(llm, BaseChatModel)