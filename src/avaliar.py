from __future__ import annotations

import json
from pathlib import Path

from core import BASE_DIR, buscar_conceitos, carregar_base, resposta_fallback


def ler_json(nome: str):
    caminho = Path(BASE_DIR) / "tests" / nome
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def testar_recuperacao(base):
    casos = ler_json("casos_teste.json")
    acertos = 0

    print("Teste 1 - recuperação da base de conhecimento\n")

    for indice, caso in enumerate(casos, start=1):
        resultados = buscar_conceitos(caso["pergunta"], base["conceitos"], limite=1)
        obtido = resultados[0]["id"] if resultados else None
        correto = obtido == caso["esperado"]
        acertos += int(correto)
        status = "OK" if correto else "ERRO"
        print(f"{indice:02d}. [{status}] {caso['pergunta']}")
        print(f"    esperado={caso['esperado']} | obtido={obtido}")

    return acertos, len(casos)


def testar_escopo(base):
    casos = ler_json("casos_seguranca.json")
    acertos = 0

    print("\nTeste 2 - perguntas fora do escopo\n")

    for indice, caso in enumerate(casos, start=1):
        resultados = buscar_conceitos(caso["pergunta"], base["conceitos"], limite=1)
        sem_contexto = not resultados
        resposta = resposta_fallback(resultados, base["exercicios"])
        admite_limite = "não tem conteúdo suficiente" in resposta.lower()
        correto = sem_contexto and admite_limite
        acertos += int(correto)
        status = "OK" if correto else "ERRO"
        print(f"{indice:02d}. [{status}] {caso['pergunta']}")
        print(f"    sem_contexto={sem_contexto} | resposta_segura={admite_limite}")

    return acertos, len(casos)


def main() -> None:
    base = carregar_base()

    acertos_rec, total_rec = testar_recuperacao(base)
    acertos_seg, total_seg = testar_escopo(base)

    total_acertos = acertos_rec + acertos_seg
    total = total_rec + total_seg

    print("\nResumo")
    print(f"Recuperação top-1: {acertos_rec}/{total_rec} ({acertos_rec / total_rec * 100:.1f}%)")
    print(f"Segurança de escopo: {acertos_seg}/{total_seg} ({acertos_seg / total_seg * 100:.1f}%)")
    print(f"Total automatizado: {total_acertos}/{total} ({total_acertos / total * 100:.1f}%)")


if __name__ == "__main__":
    main()
