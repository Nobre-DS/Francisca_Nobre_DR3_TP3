# TP3 — Agente de estudos em Ciência de Dados (ReAct + Memória + Tools)

**Disciplina:** Desenvolvimento de Data-Driven Apps com Python — DR3 TP3  
**Autoria:** Francisca Nobre  
**Situação:** aplicação implementada e testada no VS Code em 22/11/2026. Ferramentas externas, integração LangChain/Groq, memória conversacional e registro de ações/observações ReAct validados com capturas de tela. Projeto publicado em repositório público no GitHub: https://github.com/Nobre-DS/Francisca_Nobre_DR3_TP3. O envio do ZIP ao Moodle deve ser confirmado separadamente.

## 1. Problema, objetivo e público-alvo

**Problema:** uma pessoa no início da graduação em Ciência de Dados precisa consultar conceitos e procurar livros em fontes distintas e, a cada pergunta, costuma ter de repetir suas preferências de estudo.

**Objetivo:** reunir consultas técnicas e busca bibliográfica em uma interface conversacional, permitindo decisões sobre uso de ferramentas e aproveitamento do histórico no mesmo atendimento.

**Público-alvo:** estudantes iniciantes de Ciência de Dados e Inteligência Artificial.

**Funcionalidades:** (1) pesquisa de conceitos na Wikipédia em português; (2) busca de livros na Open Library; (3) combinação das ferramentas via agente LangChain; (4) memória de curto prazo com `InMemorySaver` por `thread_id`; (5) interface de linha de comando; (6) mensagens de erro compreensíveis.

## 2. Tecnologias e arquitetura

- Python 3.11; LangChain e LangGraph (`create_agent`), Groq (`ChatGroq`, modelo `openai/gpt-oss-20b`), `InMemorySaver`, `requests`, `certifi` e `python-dotenv`.
- APIs externas públicas: [Wikipédia](https://www.mediawiki.org/wiki/REST_API) (consulta de resumo) e [Open Library](https://openlibrary.org/developers/api) (pesquisa de livros). Ambas acessadas via HTTP real, sem chaves próprias.
- O uso de Groq exige `GROQ_API_KEY` válida. Pode haver limites ou indisponibilidade conforme plano e modelo.

```text
Usuário (linha de comando)
        |
        v
   app.py / responder(pergunta, thread_id)
        |
        v
LangChain create_agent + ChatGroq + InMemorySaver
        |
        v
 [Decisão] -> [Ação: consultar_conceito / buscar_livros]
      ^                  |
      |                  v
      +---- [Observação / resultado das APIs externas]
        |
        v
    Resposta fundamentada + histórico da sessão
```

**ReAct:** o agente alterna seleção de ação, execução de ferramenta e observação dos resultados, podendo repetir o ciclo. Isso é uma descrição do comportamento operacional, não uma exposição de raciocínio privado do modelo. `create_agent` usa a execução de ferramentas da infraestrutura LangChain/LangGraph.

**Memória:** `InMemorySaver` retém mensagens por `thread_id` enquanto o processo estiver ativo; **não persiste após fechar o programa**. Sessões diferentes têm históricos separados.

## 3. Estrutura de arquivos

```text
Francisca_Nobre_DR3_TP3/
  app.py                   # Interface de linha de comando
  diagnostico_tools.py      # Verificações de rede das duas APIs
  src/
    __init__.py
    agente.py              # Modelo, agente, sessão e memória
    ferramentas.py         # Duas tools externas
  tests/
    test_ferramentas.py    # Testes locais sem rede/API
  docs/
    PLANO_DE_TESTES.md     # Casos de uso e resultados observados
    evidencias/             # Capturas reais do VS Code (sem chaves)
  requirements.txt
  .env.example
  .gitignore
  README.md
```

## 4. Como executar no macOS (VS Code)

Na pasta do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Abra `.env` e substitua `sua_chave_aqui` pela sua chave Groq. **Nunca envie `.env` ao GitHub ou ao Moodle.** A chave utilizada no TP2 pode ser reutilizada enquanto válida.

```bash
python app.py
```

Digite perguntas. Para encerrar, use `sair`. Após cada resposta, o terminal apresenta o **REGISTRO DE AÇÕES (ReAct)**, com as chamadas das ferramentas e a confirmação das observações recebidas. O registro é baseado nas mensagens efetivamente retornadas pelo agente (`tool_calls`/`ToolMessage`); não mostra pensamentos privados ou inferências não observáveis.

**Testes locais sem gastar tokens:**

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py src tests
```

## 5. Ferramentas integradas

| Nome Python | Descrição | Função e fonte externa |
|---|---|---|
| `consultar_conceito` | Obtém breve descrição fundamentada de um termo | HTTP GET Wikipédia Action API; devolve texto e URL |
| `buscar_livros` | Busca até 3 livros sobre um assunto | HTTP GET Open Library; devolve títulos, autores, ano quando disponível e links |

Tratamento de erros: timeout de oito segundos; tamanho máximo da resposta; validação de campos; exceções de rede capturadas; entradas vazias rejeitadas; nenhuma credencial embutida no código.

### Diagnóstico de problemas de rede (versão 1.1)

Se as ferramentas informarem indisponibilidade, execute no terminal, com `.venv` ativado:

```bash
python -m pip install -r requirements.txt --upgrade
python diagnostico_tools.py
```

Esse diagnóstico consulta as duas APIs **sem gastar créditos Groq** e apresenta a causa provável (HTTP, SSL, DNS ou timeout). Se ambas falharem, verifique internet, VPN e bloqueios da rede; nunca desative a verificação de certificados (`verify=False`). A correção usa `requests` e os certificados de `certifi`, além de pesquisa por termo na Wikipédia para consultas como "machine learning".

## 6. Casos de uso testados e resultados observados

**Data dos testes: 22/11/2026; ambiente: VS Code no macOS; modelo: `openai/gpt-oss-20b` via Groq.** Os registros abaixo correspondem às capturas reais enviadas pela estudante, não a saídas simuladas.

| Caso | Pergunta ou ação | Resultado efetivamente observado | Evidência |
|---|---|---|---|
| CT01 | Consultar conceito de aprendizado de máquina | Diagnóstico das tools obteve resumo da Wikipédia e URL da fonte; agente incluiu explicação e fonte em consulta conjunta | `docs/evidencias/CT01_CT02_diagnostico.png`, `CT03_duas_ferramentas.png` |
| CT02 | Buscar livros de Python | Diagnóstico da Open Library retornou três títulos com autores, ano e links | `docs/evidencias/CT01_CT02_diagnostico.png` |
| CT03 | Consultar Wikipédia e dois livros numa só pergunta | Agente respondeu com explicação, link Wikipédia e dois livros da Open Library; ambas as fontes apareceram na mesma resposta | `docs/evidencias/CT03_duas_ferramentas.png` |
| CT04 | Pergunta de continuidade: "Dos dois livros que você acabou de recomendar, qual foi publicado primeiro?" | Na mesma sessão, o agente respondeu "Learning Python — 1999", sem receber novamente os títulos, demonstrando uso do histórico conversacional | `docs/evidencias/CT04_memoria.png` |
| CT05 | Falha temporária das APIs | Primeiro teste real retornou indisponibilidade das duas fontes, e o programa continuou funcionando; após correção HTTPS, o diagnóstico das APIs teve sucesso | Primeiros registros da sessão, seguidos pelo diagnóstico positivo |
| CT06 | Registro operacional ReAct com duas ferramentas | O terminal exibiu chamadas e resultados recebidos de `consultar_conceito` e `buscar_livros`, após consulta conjunta | `docs/evidencias/CT06_registro_react.png` |

**Evidência específica do ciclo ReAct — validada em 22/11/2026:** a estudante executou novamente a aplicação no Mac. No terminal, o agente consultou a Wikipédia e a Open Library numa única solicitação, respondeu com fontes e exibiu o registro efetivo de **AÇÃO** e **OBSERVAÇÃO** para `consultar_conceito` e `buscar_livros`. Evidência: `docs/evidencias/CT06_registro_react.png`. O registro representa chamadas e retornos das ferramentas, sem expor o raciocínio privado do modelo.

**Limitações:** títulos e metadados dependem de APIs públicas e podem mudar. Os testes com mocks não substituem o ensaio real do LLM. A memória é volátil e termina ao encerrar o processo. O agente auxilia a pesquisa, mas as fontes devem ser conferidas.

## 7. Reflexão: agente versus abordagem manual

Sem o agente, o estudante precisa consultar separadamente enciclopédia e catálogo bibliográfico, reunir links, e lembrar suas preferências em cada pesquisa. Com o agente ReAct, uma mesma pergunta pode levar ao uso de ambas as ferramentas, sendo seus resultados combinados numa resposta; a memória da sessão permite continuidade. Esse ganho é arquitetural e deve ser confirmado por testes práticos. Fontes externas devem sempre ser conferidas, pois resultados podem conter falhas.

## 8. Referências e declaração de uso de IA

- Aulas ministradas por Tiago Xavier, Desenvolvimento de Data-Driven Apps com Python, transcrições de 03, 06, 10, 13 e 21 nov. 2026 (materiais da disciplina): ferramentas; criação de agentes; ciclo ReAct; `InMemorySaver`, `thread_id` e memória de curto prazo.
- [LangChain — Agents](https://docs.langchain.com/oss/python/langchain/agents).
- [LangChain — Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory).
- [Groq — API documentation](https://console.groq.com/docs/overview).
- [MediaWiki REST API](https://www.mediawiki.org/wiki/REST_API).
- [Open Library API](https://openlibrary.org/developers/api).

**Uso de IA generativa:** ChatGPT (OpenAI, GPT-6), em 22/11/2026, utilizado como apoio à interpretação do enunciado e das transcrições, à elaboração inicial do código, dos testes, da documentação e à revisão de boas práticas. A estudante deve executar, analisar e validar o projeto antes de submetê-lo. O modelo acessado na aplicação é `openai/gpt-oss-20b` via Groq.
