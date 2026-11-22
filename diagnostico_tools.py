"""Verifica as duas APIs sem usar chave Groq, para facilitar o diagnóstico."""
from src.ferramentas import consultar_conceito, buscar_livros


def main():
    print("=== Teste direto de ferramentas (sem consumir tokens Groq) ===")
    for nome, ferramenta, argumento in [
        ("WIKIPÉDIA", consultar_conceito, {"conceito": "machine learning"}),
        ("OPEN LIBRARY", buscar_livros, {"assunto": "Python programming beginners"}),
    ]:
        print(f"\n--- {nome} ---", flush=True)
        try:
            print(ferramenta.invoke(argumento), flush=True)
        except Exception as erro:
            print(f"Erro inesperado: {type(erro).__name__}: {erro}", flush=True)


if __name__ == "__main__":
    main()
