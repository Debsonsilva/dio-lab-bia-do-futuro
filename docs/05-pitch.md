# 5. Pitch - roteiro de até 3 minutos

## 1. O problema

Eu escolhi trabalhar com uma situação que acontece comigo estudando Python. Muitas vezes a teoria parece simples durante a aula, mas na hora de fazer um exercício aparece uma dúvida pequena e ela bloqueia todo o raciocínio.

Pesquisar na internet ajuda, mas também é comum cair em respostas maiores e mais avançadas do que o assunto que eu estou tentando aprender naquele momento.

## 2. A solução

O projeto que eu criei se chama **PyMentor**.

Ele é um assistente voltado para Python iniciante. A diferença é que ele não manda qualquer pergunta direto para uma IA. Primeiro ele procura o assunto em uma base de conhecimento que eu organizei em JSON.

Se encontra conteúdo relacionado, monta um contexto com explicação, exemplo, erros comuns e, quando existe, um exercício. Só depois esse contexto é enviado para um modelo local pelo Ollama.

No prompt eu defini que o agente deve explicar de forma simples, evitar inventar informação e dar uma dica antes de entregar a solução de um desafio.

Se a pergunta estiver fora do que a base conhece, ele admite a limitação.

## 3. Demonstração

Na gravação eu mostraria três situações.

Primeiro:

```text
Para que serve o % em Python?
```

O PyMentor deve recuperar o assunto de resto da divisão e explicar com um exemplo simples.

Depois:

```text
Não entendi texto[::2].
```

Nesse caso ele recupera fatiamento e explica a ideia do passo.

Por último eu perguntaria:

```text
Qual a previsão do tempo amanhã?
```

A aplicação não encontra contexto suficiente e informa que esse assunto está fora da base.

## 4. Diferencial e aprendizado

O principal ponto do projeto para mim foi entender que um assistente não é somente colocar uma pergunta em uma LLM.

Eu precisei pensar em como organizar conhecimento, selecionar contexto, criar regras no prompt e testar quando o agente deveria ou não responder.

Também criei testes automáticos para a busca. Hoje são 20 perguntas de Python e 5 perguntas fora do escopo, com os 25 casos passando na versão atual.

Como evolução, eu adicionaria mais assuntos e depois compararia essa busca simples com uma busca semântica usando embeddings.

## Checklist antes de gravar

- [ ] Abrir o PyMentor funcionando no Streamlit
- [ ] Mostrar uma pergunta sobre `%`
- [ ] Mostrar uma pergunta sobre fatiamento
- [ ] Mostrar uma pergunta fora do escopo
- [ ] Mostrar rapidamente a pasta `data/`
- [ ] Mostrar o resultado de `python src/avaliar.py`
- [ ] Manter o vídeo abaixo de 3 minutos

## Link do vídeo

Adicionar aqui depois de gravar:

```text
LINK_DO_VIDEO
```
