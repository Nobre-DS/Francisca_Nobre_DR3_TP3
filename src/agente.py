"""Criação do agente orientado por ferramentas com memória de sessão."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

from .ferramentas import FERRAMENTAS

load_dotenv()

PROMPT_SISTEMA = """Você é um assistente acadêmico para estudantes iniciantes de Ciência de Dados e IA.
Seu objetivo é explicar conceitos e recomendar livros de forma verificável.
Siga o ciclo ReAct operacional: analise a solicitação, escolha uma ferramenta quando
necessário, observe os dados retornados e decida se precisa de outra ferramenta
antes de responder. Não exiba raciocínio privado; apresente somente conclusões,
fontes e ações utilizadas. Quando pedirem explicação de um conceito, use
consultar_conceito. Quando pedirem livros, use buscar_livros. Se pedirem ambos,
use as duas ferramentas. Use as preferências já informadas nesta sessão para
adaptar a resposta sem inventar fatos. Não invente títulos, autores ou URLs.
Se a fonte estiver indisponível, informe a limitação. Não solicite dados pessoais.
Responda em português claro e objetivo."""

MEMORIA = InMemorySaver()


@lru_cache(maxsize=1)
def criar_agente():
    chave = os.getenv("GROQ_API_KEY", "").strip()
    if not chave or chave in {"sua_chave_aqui", "CHAVE_OCULTADA"}:
        raise RuntimeError("Configure GROQ_API_KEY no arquivo .env (não publique essa chave).")
    modelo = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        temperature=0,
        timeout=30,
        max_retries=1,
    )
    return create_agent(model=modelo, tools=FERRAMENTAS,
                        system_prompt=PROMPT_SISTEMA, checkpointer=MEMORIA)


def registrar_acoes_react(mensagens: list, pergunta: str) -> str:
    """Registra apenas chamadas/retornos de tools no turno atual; nunca expõe raciocínio privado."""
    inicio = 0
    for indice, mensagem in enumerate(mensagens):
        if (getattr(mensagem, "type", "") == "human"
                and getattr(mensagem, "content", None) == pergunta.strip()):
            inicio = indice + 1

    eventos = []
    for mensagem in mensagens[inicio:]:
        for chamada in (getattr(mensagem, "tool_calls", None) or []):
            nome = chamada.get("name", "desconhecida")
            if nome in {"consultar_conceito", "buscar_livros"}:
                eventos.append(f"AÇÃO: chamada da ferramenta {nome}")
        if getattr(mensagem, "type", "") == "tool":
            nome = getattr(mensagem, "name", "ferramenta")
            conteudo = str(getattr(mensagem, "content", ""))
            falhou = any(marcador in conteudo.lower() for marcador in (
                "falhou:", "não retornou", "nenhum livro", "sem resultados"))
            estado = "falha ou resultado indisponível" if falhou else "resultado recebido"
            eventos.append(f"OBSERVAÇÃO: {nome} — {estado}")
    if not eventos:
        return "REGISTRO DE AÇÕES: nenhuma ferramenta externa chamada neste turno."
    return "REGISTRO DE AÇÕES (ReAct):\n" + "\n".join("  - " + e for e in eventos)


def responder(pergunta: str, sessao: str, agente=None, exibir_acoes: bool = False) -> str:
    """Executa o ciclo ReAct usando thread_id para recuperar o contexto anterior."""
    if not isinstance(pergunta, str) or not pergunta.strip():
        raise ValueError("Digite uma pergunta não vazia.")
    if len(pergunta) > 1500:
        raise ValueError("A pergunta deve conter até 1.500 caracteres.")
    if not isinstance(sessao, str) or not sessao.strip() or len(sessao) > 80:
        raise ValueError("Identificador de sessão inválido.")
    instancia = agente if agente is not None else criar_agente()
    resultado = instancia.invoke(
        {"messages": [{"role": "user", "content": pergunta.strip()}]},
        config={"configurable": {"thread_id": sessao}, "recursion_limit": 12},
    )
    mensagens = resultado.get("messages", [])
    if not mensagens:
        raise RuntimeError("O agente não retornou mensagens.")
    conteudo = mensagens[-1].content
    resposta = conteudo.strip() if isinstance(conteudo, str) else str(conteudo)
    if exibir_acoes:
        resposta += "\n\n" + registrar_acoes_react(mensagens, pergunta)
    return resposta
