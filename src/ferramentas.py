"""Consultas a duas APIs públicas, com erros observáveis e respostas verificáveis."""
import logging
import os
from urllib.parse import quote

import certifi
import requests
from langchain_core.tools import tool

LOG = logging.getLogger(__name__)
TEMPO_LIMITE = (5, 15)  # conexão, leitura (segundos)
TAMANHO_MAXIMO = 300_000
HEADERS = {
    "User-Agent": "FranciscaNobre-TP3-Academico/1.1 (contato: projeto acadêmico)",
    "Accept": "application/json",
}


class FalhaConsultaExterna(RuntimeError):
    """Indica falha de rede, HTTP ou formato da resposta."""


def _obter_json(url: str, parametros: dict | None = None) -> dict:
    """Busca JSON via HTTPS com cadeia de certificados do certifi.

    Nunca desativa a verificação TLS. A mensagem preserva a causa do erro
    (sem imprimir credenciais; essas APIs não usam token).
    """
    try:
        with requests.get(
            url,
            params=parametros,
            headers=HEADERS,
            timeout=TEMPO_LIMITE,
            verify=certifi.where(),
            stream=True,
        ) as resposta:
            resposta.raise_for_status()
            recebido = bytearray()
            for bloco in resposta.iter_content(chunk_size=8192):
                recebido.extend(bloco)
                if len(recebido) > TAMANHO_MAXIMO:
                    raise FalhaConsultaExterna("Resposta maior que 300 KB.")
            dados = resposta.json() if not recebido else __import__('json').loads(recebido.decode('utf-8'))
            if not isinstance(dados, dict):
                raise FalhaConsultaExterna("JSON não é um objeto.")
            return dados
    except requests.exceptions.SSLError as erro:
        raise FalhaConsultaExterna(
            "Erro de certificado HTTPS (SSL). Atualize certifi/requests e confira certificados ou proxy da rede."
        ) from erro
    except requests.exceptions.Timeout as erro:
        raise FalhaConsultaExterna("Tempo limite excedido ao consultar a API.") from erro
    except requests.exceptions.HTTPError as erro:
        codigo = erro.response.status_code if erro.response is not None else "desconhecido"
        raise FalhaConsultaExterna(f"HTTP {codigo} retornado pela API externa.") from erro
    except requests.exceptions.ConnectionError as erro:
        raise FalhaConsultaExterna("Falha de conexão ou DNS com a API externa.") from erro
    except (ValueError, UnicodeError) as erro:
        raise FalhaConsultaExterna("A API não retornou JSON válido.") from erro
    except requests.exceptions.RequestException as erro:
        raise FalhaConsultaExterna(f"Erro de requisição: {type(erro).__name__}.") from erro


@tool
def consultar_conceito(conceito: str) -> str:
    """Busca na Wikipédia em português um conceito e devolve seu resumo e fonte. Use para explicar termos de Ciência de Dados."""
    termo = conceito.strip()
    if not termo or len(termo) > 100:
        return "Informe um conceito válido com até 100 caracteres."
    # Generator search localiza também termos em inglês, como 'machine learning'.
    parametros = {
        "action": "query", "generator": "search", "gsrsearch": termo,
        "gsrlimit": 1, "prop": "extracts", "exintro": 1,
        "explaintext": 1, "exchars": 1600, "format": "json", "formatversion": 2,
    }
    try:
        dados = _obter_json("https://pt.wikipedia.org/w/api.php", parametros)
    except FalhaConsultaExterna as erro:
        LOG.warning("Wikipédia: %s", erro)
        return f"Consulta à Wikipédia falhou: {erro} Não invente informações de fonte externa."
    paginas = dados.get("query", {}).get("pages", [])
    pagina = paginas[0] if paginas and isinstance(paginas[0], dict) else {}
    titulo, resumo = pagina.get("title", ""), pagina.get("extract", "")
    if not resumo:
        return "A Wikipédia não retornou um resumo para esse termo; tente outra expressão."
    fonte = "https://pt.wikipedia.org/wiki/" + quote(titulo.replace(" ", "_"), safe="")
    return f"Conceito: {titulo}\nResumo: {resumo[:1500]}\nFonte: {fonte}"


@tool
def buscar_livros(assunto: str) -> str:
    """Pesquisa livros na Open Library e retorna títulos, autores e links reais; use para sugestões de leitura."""
    termo = assunto.strip()
    if not termo or len(termo) > 100:
        return "Informe um assunto válido com até 100 caracteres."
    parametros = {"q": termo, "limit": 3, "fields": "key,title,author_name,first_publish_year"}
    try:
        dados = _obter_json("https://openlibrary.org/search.json", parametros)
    except FalhaConsultaExterna as erro:
        LOG.warning("Open Library: %s", erro)
        return f"Consulta à Open Library falhou: {erro} Não invente títulos nem autores."
    livros = dados.get("docs", [])
    if not isinstance(livros, list) or not livros:
        return "Nenhum livro encontrado na Open Library para esse assunto."
    linhas = []
    for item in livros[:3]:
        if not isinstance(item, dict):
            continue
        chave = item.get("key", "")
        if not isinstance(chave, str) or not chave.startswith("/works/"):
            continue
        autores = item.get("author_name") or []
        autor = ", ".join(str(a) for a in autores[:2]) if isinstance(autores, list) else "não informado"
        linhas.append(
            f"Título: {item.get('title', 'não informado')} | Autor(es): {autor} | "
            f"Ano: {item.get('first_publish_year', 'não informado')} | Fonte: https://openlibrary.org{chave}"
        )
    return "\n".join(linhas) if linhas else "Sem resultados válidos na Open Library."


FERRAMENTAS = [consultar_conceito, buscar_livros]
