# Plano de testes práticos — TP3

Testes realizados em **22/11/2026**, no VS Code/macOS, com as APIs Wikipédia e Open Library e o modelo Groq `openai/gpt-oss-20b`. Capturas em `docs/evidencias/`.

| ID | Caso | Resultado observado | Situação |
|---|---|---|---|
| CT01 | Consulta de conceito | O diagnóstico retornou resumo do aprendizado de máquina e link Wikipédia; no agente a resposta conjunta citou a fonte | Aprovado para consulta e retorno |
| CT02 | Busca bibliográfica | O diagnóstico apresentou títulos, autores, anos e links Open Library | Aprovado para consulta e retorno |
| CT03 | Uma pergunta exigindo duas ferramentas | Agente apresentou informações de Wikipédia e dois livros Open Library | Aprovado na integração de resultados; registro AÇÃO/OBSERVAÇÃO ainda necessita captura |
| CT04 | Seguimento sem repetir títulos | Agente respondeu “Learning Python — 1999” com base no turno anterior | Aprovado para memória de sessão |
| CT05 | Falha temporária de serviço | App permaneceu funcionando quando APIs indisponíveis; correção restaurou as consultas | Tratamento de erro observado |

## Evidência operacional do ReAct ainda a registrar

O novo código mostra no terminal `REGISTRO DE AÇÕES (ReAct)`, com nomes de chamadas (`tool_calls`) e mensagens de retorno das ferramentas (`ToolMessage`). Este **registro de ações é auditável**, diferentemente da exposição de raciocínio interno do modelo, que não é necessário nem adequado.

Execute `python app.py` e digite:

> Consulte a Wikipédia para explicar machine learning e pesquise na Open Library dois livros sobre Python. Cite as fontes.

Ao final da resposta, registre captura com as linhas `AÇÃO: chamada da ferramenta consultar_conceito`, `OBSERVAÇÃO: consultar_conceito`, `AÇÃO: chamada da ferramenta buscar_livros` e `OBSERVAÇÃO: buscar_livros`, conforme ações realmente executadas. Se alguma não aparecer, não considerar comprovada; investigar a escolha de ferramentas do agente. Não inventar mensagens para preencher lacunas.

## Comparação com processo manual

Sem agente: consultas independentes à Wikipédia e à Open Library, seleção dos livros e cópia manual das fontes; em seguimentos, lembrar os títulos da pesquisa anterior. Com agente: consulta unificada e recuperação do histórico durante a mesma sessão. O ganho foi observado qualitativamente; não houve cronometragem comparativa.
