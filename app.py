"""Interface simples de linha de comando para o TP3."""
from uuid import uuid4

from src.agente import responder


def main():
    sessao = uuid4().hex
    print("ASSISTENTE DE ESTUDOS EM CIÊNCIA DE DADOS — TP3")
    print("Digite uma pergunta. Use 'sair' para encerrar.")
    print("A memória permanece durante esta execução do programa.\n")
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nConversa encerrada.")
            break
        if pergunta.lower() in {"sair", "exit"}:
            print("Conversa encerrada.")
            break
        if not pergunta:
            print("Digite sua pergunta.")
            continue
        try:
            print("\nAgente:", responder(pergunta, sessao, exibir_acoes=True), "\n")
        except (ValueError, RuntimeError) as erro:
            print(f"Aviso: {erro}\n")
        except Exception:
            print("Erro de comunicação com o modelo ou serviço. Verifique sua conexão e limites da API.\n")


if __name__ == "__main__":
    main()
