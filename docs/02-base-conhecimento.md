# 2. Base de Conhecimento

## Dados usados

Eu não aproveitei os arquivos financeiros do repositório original porque o tema do meu agente mudou. Montei uma base pequena voltada para Python iniciante.

| Arquivo | Formato | Uso |
|---|---|---|
| `conceitos_python.json` | JSON | Explicações e exemplos dos assuntos |
| `exercicios.json` | JSON | Desafios, dicas e soluções de referência |
| `erros_comuns.json` | JSON | Erros que costumam aparecer em cada assunto |

## Conteúdo da base

A primeira versão possui 20 conceitos. Eu preferi começar com assuntos que aparecem com frequência nos primeiros exercícios de Python, por exemplo:

- variáveis;
- tipos de dados;
- `input()`;
- f-strings;
- `%` e `//`;
- condições;
- listas;
- fatiamento;
- repetição;
- funções;
- erros básicos.

Também incluí exemplos que lembram situações que eu mesmo encontrei estudando, como remover duplicados mantendo a ordem e entender `lista[1:4]` ou `texto[::2]`.

## Estrutura de um conceito

Exemplo simplificado:

```json
{
  "id": "modulo",
  "titulo": "Operador de resto %",
  "aliases": ["modulo", "resto da divisão", "%"],
  "palavras_chave": ["resto", "par ou impar"],
  "resumo": "O operador % devolve o resto de uma divisão.",
  "explicacao": "Em 10 % 3, o resultado é 1...",
  "exemplo": "saldo = 102\nsaldo %= 4\nprint(saldo)"
}
```

Os campos `aliases` e `palavras_chave` existem para facilitar a busca mesmo quando a pergunta não usa exatamente o título cadastrado.

## Como a busca funciona

A função `buscar_conceitos()` fica em `src/core.py`.

Ela faz uma busca simples por pontuação. Alguns fatores aumentam a pontuação de um tópico:

- título aparecendo na pergunta;
- alias encontrado;
- palavra-chave encontrada;
- palavras em comum entre pergunta e conteúdo;
- símbolos importantes, como `%`, `//` ou uma expressão de fatiamento.

Depois disso, os tópicos com maior pontuação são usados como contexto.

Não usei embeddings nesta versão porque quis entender primeiro a mecânica da recuperação de informação sem esconder essa parte em outra biblioteca.

## Integração com o prompt

Somente os resultados encontrados são transformados em contexto. Um trecho fica parecido com isto:

```text
TÓPICO: Operador de resto %
RESUMO: O operador % devolve o resto de uma divisão.
EXPLICAÇÃO: Em 10 % 3, o resultado é 1...
EXEMPLO:
saldo = 102
saldo %= 4
print(saldo)
```

Erros comuns e um desafio relacionado também podem ser anexados ao mesmo contexto.

## O que acontece quando não encontra nada

Se a busca não atingir a pontuação mínima, a aplicação não inventa um assunto próximo. Ela devolve uma mensagem dizendo que a base ainda não possui conteúdo suficiente.

Foi a forma que encontrei de deixar a limitação do protótipo explícita e, ao mesmo tempo, testar uma estratégia simples contra alucinação.
