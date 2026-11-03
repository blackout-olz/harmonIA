import sys
from src.agent import executar_agente, criar_agente

def modo_interativo():
    print("=" * 60)
    print("🎵 HarmonIA — Assistente Virtual Empório da Música")
    print("Digite sua pergunta abaixo. Para sair, digite 'sair' ou 'exit'.")
    print("=" * 60 + "\n")

    # Instancia o agente em modo verbose se desejar ver o raciocínio e ferramentas
    agente = criar_agente(verbose=True)

    while True:
        try:
            user_input = input("\nCliente > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\nHarmonIA: Obrigado por consultar a Empório da Música! Até logo.")
                break

            resposta = agente.invoke({"input": user_input})
            print(f"\nHarmonIA > {resposta.get('output', 'Sem resposta.')}")

        except KeyboardInterrupt:
            print("\n\nSessão encerrada.")
            break
        except Exception as e:
            print(f"\n[Erro]: {str(e)}")

if __name__ == "__main__":
    # Se o usuário passar a pergunta como argumento: python main.py "Qual o preço do violão?"
    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"Pergunta: {pergunta}\n")
        resposta = executar_agente(pergunta)
        print(f"HarmonIA: {resposta}")
    else:
        modo_interativo()