from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("PYMENTOR_MODEL", "llama3.2:3b")

STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "eu", "me", "meu", "minha", "na", "nas", "no", "nos", "o",
    "os", "para", "por", "que", "qual", "quais", "se", "serve", "um", "uma",
    "usar", "uso", "pra", "pro", "isso", "isto", "python", "funciona", "funcionar",
}


def _ler_json(caminho: Path) -> list[dict[str, Any]]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_base() -> dict[str, list[dict[str, Any]]]:
    return {
        "conceitos": _ler_json(DATA_DIR / "conceitos_python.json"),
        "exercicios": _ler_json(DATA_DIR / "exercicios.json"),
        "erros": _ler_json(DATA_DIR / "erros_comuns.json"),
    }


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9%+*/<>=!_\-\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def tokens(texto: str) -> set[str]:
    return {
        token
        for token in normalizar(texto).split()
        if len(token) > 1 and token not in STOPWORDS
    }


def _score_conceito(pergunta: str, conceito: dict[str, Any]) -> float:
    pergunta_n = normalizar(pergunta)
    pergunta_tokens = tokens(pergunta)

    titulo = normalizar(conceito["titulo"])
    aliases = [normalizar(item) for item in conceito.get("aliases", [])]
    palavras = [normalizar(item) for item in conceito.get("palavras_chave", [])]
    resumo = normalizar(conceito.get("resumo", ""))
    explicacao = normalizar(conceito.get("explicacao", ""))

    score = 0.0

    if titulo and titulo in pergunta_n:
        score += 9

    for alias in aliases:
        if not alias:
            continue
        if alias in pergunta_n:
            score += 8 if len(alias) > 2 else 4

    for palavra in palavras:
        if palavra and palavra in pergunta_n:
            score += 5

    campo_tokens = tokens(" ".join([titulo, *aliases, *palavras, resumo, explicacao]))
    intersecao = pergunta_tokens & campo_tokens
    score += len(intersecao) * 1.5

    if "%" in pergunta and conceito["id"] == "modulo":
        score += 12
    if "//" in pergunta and conceito["id"] == "divisao_inteira":
        score += 12
    if "[" in pergunta and ":" in pergunta and conceito["id"] == "fatiamento":
        score += 30
    if any(op in pergunta for op in [">=", "<=", "==", "!="]) and conceito["id"] == "comparacao":
        score += 7

    partes = set(pergunta_n.split())
    if "input" in partes and conceito["id"] == "input":
        score += 20
    if "for" in partes and conceito["id"] == "for":
        score += 20
    if "while" in partes and conceito["id"] == "while":
        score += 20

    return score


def buscar_conceitos(
    pergunta: str,
    conceitos: list[dict[str, Any]],
    limite: int = 3,
    score_minimo: float = 5.0,
) -> list[dict[str, Any]]:
    pontuados: list[tuple[float, dict[str, Any]]] = []

    for conceito in conceitos:
        score = _score_conceito(pergunta, conceito)
        if score >= score_minimo:
            item = dict(conceito)
            item["_score"] = round(score, 2)
            pontuados.append((score, item))

    pontuados.sort(key=lambda item: item[0], reverse=True)
    return [conceito for _, conceito in pontuados[:limite]]


def _itens_relacionados(
    conceito_id: str,
    itens: list[dict[str, Any]],
    limite: int = 2,
) -> list[dict[str, Any]]:
    encontrados = [item for item in itens if item.get("conceito_id") == conceito_id]
    return encontrados[:limite]


def montar_contexto(
    resultados: list[dict[str, Any]],
    exercicios: list[dict[str, Any]],
    erros: list[dict[str, Any]],
) -> str:
    if not resultados:
        return ""

    blocos: list[str] = []

    for conceito in resultados:
        conceito_id = conceito["id"]
        bloco = [
            f"TÓPICO: {conceito['titulo']}",
            f"RESUMO: {conceito['resumo']}",
            f"EXPLICAÇÃO: {conceito['explicacao']}",
            "EXEMPLO:",
            conceito["exemplo"],
        ]

        erros_do_topico = _itens_relacionados(conceito_id, erros)
        if erros_do_topico:
            bloco.append("ERROS COMUNS:")
            for item in erros_do_topico:
                bloco.append(f"- {item['erro']} Correção: {item['correcao']}")

        exercicios_do_topico = _itens_relacionados(conceito_id, exercicios, limite=1)
        if exercicios_do_topico:
            ex = exercicios_do_topico[0]
            bloco.extend(
                [
                    "DESAFIO DISPONÍVEL:",
                    ex["enunciado"],
                    f"Dica: {ex['dica']}",
                    "A solução completa está na base, mas só deve ser mostrada se o usuário pedir diretamente.",
                ]
            )

        blocos.append("\n".join(bloco))

    return "\n\n---\n\n".join(blocos)


SYSTEM_PROMPT = """
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
""".strip()


def montar_mensagens(
    pergunta: str,
    contexto: str,
    historico: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    mensagens: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if historico:
        for item in historico[-6:]:
            if item.get("role") in {"user", "assistant"} and item.get("content"):
                mensagens.append({"role": item["role"], "content": item["content"]})

    conteudo_usuario = (
        "CONTEXTO DA BASE DE CONHECIMENTO:\n"
        f"{contexto}\n\n"
        "PERGUNTA DO USUÁRIO:\n"
        f"{pergunta}"
    )
    mensagens.append({"role": "user", "content": conteudo_usuario})
    return mensagens


def ollama_disponivel(url: str = OLLAMA_URL) -> bool:
    try:
        resposta = requests.get(f"{url}/api/tags", timeout=1.2)
        return resposta.ok
    except requests.RequestException:
        return False


def perguntar_ollama(
    mensagens: list[dict[str, str]],
    modelo: str = DEFAULT_MODEL,
    url: str = OLLAMA_URL,
) -> str:
    payload = {
        "model": modelo,
        "messages": mensagens,
        "stream": False,
        "options": {"temperature": 0.25},
    }
    resposta = requests.post(f"{url}/api/chat", json=payload, timeout=120)
    resposta.raise_for_status()
    dados = resposta.json()
    return dados["message"]["content"].strip()


def resposta_fallback(
    resultados: list[dict[str, Any]],
    exercicios: list[dict[str, Any]],
) -> str:
    if not resultados:
        return (
            "Minha base ainda não tem conteúdo suficiente para responder isso com segurança. "
            "Posso ajudar com os tópicos de Python que já estão cadastrados no projeto."
        )

    conceito = resultados[0]
    partes = [
        f"**{conceito['titulo']}**",
        conceito["explicacao"],
        "```python",
        conceito["exemplo"],
        "```",
    ]

    relacionados = _itens_relacionados(conceito["id"], exercicios, limite=1)
    if relacionados:
        ex = relacionados[0]
        partes.append(f"**Desafio:** {ex['enunciado']}")
        partes.append(f"**Dica:** {ex['dica']}")

    partes.append(
        "_Ollama não está ativo, então esta resposta veio diretamente da base de conhecimento do projeto._"
    )
    return "\n\n".join(partes)
