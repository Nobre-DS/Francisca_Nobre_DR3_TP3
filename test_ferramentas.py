"""Testes sem rede: simulam respostas das APIs externas."""
import unittest
from unittest.mock import patch
from src.ferramentas import consultar_conceito, buscar_livros, FalhaConsultaExterna
from src.agente import responder


class TestarFerramentas(unittest.TestCase):
    @patch("src.ferramentas._obter_json")
    def test_consultar_conceito(self, requisitar):
        requisitar.return_value = {"title": "Python", "extract": "Linguagem de programação.",
                                    "content_urls": {"desktop": {"page": "https://pt.wikipedia.org/wiki/Python"}}}
        resultado = consultar_conceito.invoke({"conceito": "Python"})
        self.assertIn("Linguagem de programação", resultado)
        self.assertIn("https://", resultado)

    @patch("src.ferramentas._obter_json")
    def test_buscar_livros(self, requisitar):
        requisitar.return_value = {"docs": [{"key": "/works/OL123W", "title": "Livro Teste", "author_name": ["Autora Teste"], "first_publish_year": 2020}]}
        resultado = buscar_livros.invoke({"assunto": "python"})
        self.assertIn("Livro Teste", resultado)
        self.assertIn("openlibrary.org/works/OL123W", resultado)

    @patch("src.ferramentas._obter_json", side_effect=FalhaConsultaExterna("falha"))
    def test_falha_conceito(self, _):
        self.assertIn("Não foi possível", consultar_conceito.invoke({"conceito": "Python"}))

    @patch("src.ferramentas._obter_json", side_effect=FalhaConsultaExterna("falha"))
    def test_falha_livros(self, _):
        self.assertIn("Não foi possível", buscar_livros.invoke({"assunto": "Python"}))

    def test_parametro_invalido(self):
        self.assertIn("válido", consultar_conceito.invoke({"conceito": " "}))
        self.assertIn("válido", buscar_livros.invoke({"assunto": " "}))


class AgenteSimulado:
    """Dublê para verificar transporte de mensagens e identificação de sessão."""
    def __init__(self):
        self.historico = {}

    def invoke(self, payload, config):
        chave = config["configurable"]["thread_id"]
        ultima = payload["messages"][0]["content"]
        self.historico.setdefault(chave, []).append(ultima)
        return {"messages": [type("Mensagem", (), {"content": " | ".join(self.historico[chave])})()]}


class TestarInterfaceAgente(unittest.TestCase):
    def test_reutilizacao_da_mesma_sessao_com_agente_simulado(self):
        simulado = AgenteSimulado()
        self.assertEqual(responder("Estudo Python", "sessao1", simulado), "Estudo Python")
        self.assertEqual(responder("E livros?", "sessao1", simulado), "Estudo Python | E livros?")
        self.assertEqual(responder("Olá", "sessao2", simulado), "Olá")

    def test_validacao_de_entrada(self):
        with self.assertRaises(ValueError):
            responder("", "s1", AgenteSimulado())
        with self.assertRaises(ValueError):
            responder("teste", "", AgenteSimulado())
        with self.assertRaises(ValueError):
            responder("a" * 1501, "s1", AgenteSimulado())


if __name__ == "__main__":
    unittest.main()
