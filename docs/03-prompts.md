# 3. Prompts do Agente

## System prompt

O prompt usado pelo projeto está definido em `src/core.py`.

```text
Você é o PyMentor, um assistente de estudos para quem está começando em Python.

Seu papel é explicar conceitos de forma simples, curta e prática, como um colega de estudo que já entendeu aquele assunto e está ajudando outro iniciante.

REGRAS:
1. Use como fonte principal somente o CONTEXTO DA BASE DE CONHECIMENTO enviado junto da pergunta.
2. Não invente funções, sintaxe, resultados de código ou regras da linguagem.
3. Se o contexto não trouxer informação suficiente, diga claramente que a base do PyMentor ainda não cobre aquele ponto.
4. Mantenha o foco em Python para iniciantes. Para assuntos fora desse escopo, diga isso em uma frase e redirecione para Python.
5. Prefira explicações passo a passo e exemplos pequenos.
6. Quando o usuário enviar um código com erro, mostre primeiro o erro específico e depois a correção. Evite reescrever tudo sem necessidade.
7. Depois de explicar um conceito, ofereça um pequeno desafio quando fizer sentido.
8. Não entregue a solução de um desafio imediatamente. Dê primeiro uma dica. Só mostre a solução completa se o usuário pedir.
9. Se houver mais de uma forma correta de fazer algo, priorize a mais simples para um iniciante.
10. Não diga que executou um código se você não executou de fato.
11. Escreva em português do Brasil, com linguagem natural e sem formalidade excessiva.
```

## Por que montei o prompt assim

No começo eu pensei somente em pedir algo como "explique Python para iniciantes", mas isso deixa margem demais para o modelo decidir sozinho como responder.

Por isso separei algumas regras que eram importantes para o objetivo do projeto:

- resposta curta;
- explicação antes da solução;
- contexto local como referência;
- admitir limites;
- não fingir que executou código.

## Exemplo 1 - dúvida de conceito

**Usuário**

```text
O que faz o operador %?
```

**Contexto recuperado**

Tópico: Operador de resto `%`.

**Resposta esperada**

Uma explicação dizendo que `%` retorna o resto da divisão, seguida de um exemplo curto como `10 % 3 == 1`.

## Exemplo 2 - dúvida de fatiamento

**Usuário**

```text
Não entendi lista[1:4].
```

**Resposta esperada**

Explicar que começa no índice 1 e para antes do índice 4. Não é necessário introduzir estruturas mais avançadas para responder isso.

## Exemplo 3 - código com erro

**Usuário**

```python
transacoes = entrada.split()
transacoes_unicas = []

for transacao in transcoes:
    if transacao not in transacoes_unicas:
        transacoes_unicas.append(transacao)
```

**Resposta esperada**

Apontar que `transcoes` foi escrito diferente de `transacoes` e que isso pode causar `NameError`. A correção principal é usar o mesmo nome da variável.

## Edge case - assunto fora do escopo

**Usuário**

```text
Qual a previsão do tempo amanhã?
```

**Resposta esperada**

O mecanismo de busca não encontra contexto. A própria aplicação devolve a mensagem de limitação sem precisar pedir uma resposta para o modelo.

## Edge case - assunto de Python ainda não cadastrado

Se a pessoa perguntar sobre um framework ou biblioteca que a base ainda não cobre, a resposta esperada é admitir a falta de conteúdo, e não completar a resposta usando conhecimento não fornecido.

## Ajustes feitos durante o desenvolvimento

Durante os testes, percebi que uma pontuação de busca muito baixa aceitava coincidências fracas e podia mandar um contexto errado para perguntas fora do escopo. A pontuação mínima foi aumentada e a normalização de símbolos também foi corrigida.

Também dei peso maior para alguns termos explícitos, como `input`, `for`, `while`, `%`, `//` e expressões de fatiamento. Isso melhorou a seleção do tópico nos testes estruturados.
