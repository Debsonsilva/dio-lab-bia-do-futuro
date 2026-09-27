# 4. Avaliação e Métricas

## O que eu decidi medir

Como o projeto possui uma parte determinística antes da LLM, comecei avaliando essa parte. Se o sistema recuperar o conteúdo errado, até um modelo bom recebe um contexto ruim.

As duas métricas automatizadas desta versão são:

| Métrica | O que verifica |
|---|---|
| Recuperação top-1 | Se o primeiro tópico encontrado é o esperado para a pergunta |
| Segurança de escopo | Se perguntas claramente fora de Python ficam sem contexto e recebem a mensagem de limitação |

## Casos de teste

Os arquivos ficam em `tests/`.

### Recuperação

Foram criadas 20 perguntas cobrindo os assuntos da base. Alguns exemplos:

- "Para que serve o operador %?"
- "Não entendi lista[1:4]"
- "Como percorrer uma lista com for?"
- "Apareceu NameError, o que significa?"

### Fora do escopo

Foram usadas 5 perguntas que o PyMentor não deveria tentar responder:

- previsão do tempo;
- futebol;
- receita culinária;
- investimento;
- medicamento.

## Como executar

```bash
python src/avaliar.py
```

## Resultado atual

Resultado registrado em `tests/resultado_avaliacao.txt`:

```text
Recuperação top-1: 20/20 (100.0%)
Segurança de escopo: 5/5 (100.0%)
Total automatizado: 25/25 (100.0%)
```

### Interpretação

O resultado de 100% significa que **os 25 casos definidos para a lógica local passaram**. Não significa que o PyMentor tem 100% de precisão em qualquer pergunta e também não mede sozinho a qualidade das frases geradas pelo modelo.

Essa diferença é importante porque a saída da LLM é probabilística. Mesmo recebendo o contexto correto, ela ainda pode variar a resposta.

## Avaliação manual da resposta gerada

Para testar a parte de linguagem, usei estes critérios como checklist:

| Critério | Pergunta para avaliar |
|---|---|
| Assertividade | Respondeu realmente o que foi perguntado? |
| Clareza | Um iniciante consegue acompanhar a explicação? |
| Fidelidade ao contexto | A resposta ficou dentro do conteúdo recuperado? |
| Didática | Explicou antes de simplesmente entregar uma solução? |
| Segurança | Admitiu quando não havia informação suficiente? |

A ideia para uma próxima versão é pedir para outras pessoas que estejam estudando Python darem notas de 1 a 5 nesses critérios. Nesta entrega eu mantive os resultados numéricos somente para os testes que realmente podem ser repetidos automaticamente.

## Problemas encontrados durante o teste

Um erro interessante apareceu na primeira versão da normalização. Um marcador de fatiamento formado apenas por símbolos acabava virando um espaço em branco. Como um espaço existe em praticamente toda pergunta, o tópico de fatiamento recebia pontos até para perguntas como previsão do tempo.

Depois de aplicar `strip()` no resultado normalizado e repetir os testes, os cinco casos fora do escopo passaram.

Esse teste acabou sendo útil porque mostrou um problema que olhando só para a interface poderia passar despercebido.
