"""Tradução dos bloqueios usando exclusivamente contagens por categoria."""
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def traduzir_bloqueio(bloqueio):
    chave = os.environ.get("GEMINI_API_KEY")
    modelo = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    if not chave:
        return "IA indisponível", "Configure GEMINI_API_KEY para gerar a explicação."
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", modelo):
        return "IA indisponível", "Confira o identificador do modelo."
    tipos = bloqueio["tipos_bloqueados"]
    resumo = {tipo: int(tipos[tipo]) for tipo in ("CPF", "Telefone", "Senha", "Saúde") if tipo in tipos}
    if not resumo:
        return "Sem bloqueios", "Nenhum bloqueio para explicar nesta execução."
    prompt = (
        "Explique em até duas frases em português brasileiro, para um cidadão sem conhecimento técnico, "
        "o resultado desta simulação. Um filtro impediu que mensagens com dados pessoais fossem "
        "gravadas em um registro de teste. Use linguagem simples. Não invente ataques ou vazamentos. "
        "Quantidade de mensagens bloqueadas por categoria: " + json.dumps(resumo, ensure_ascii=False)
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    corpo = {"contents": [{"parts": [{"text": prompt}]}]}
    pedido = Request(url, data=json.dumps(corpo).encode(),
                     headers={"Content-Type": "application/json", "x-goog-api-key": chave})
    try:
        with urlopen(pedido, timeout=25) as resposta:
            candidato = json.load(resposta)["candidates"][0]
        if candidato.get("finishReason") != "STOP":
            raise ValueError("Resposta incompleta")
        partes = candidato["content"]["parts"]
        texto = " ".join(p["text"] for p in partes if not p.get("thought") and p.get("text")).strip()
        if not texto:
            raise ValueError("Resposta vazia")
        return f"Gerado por Gemini • {modelo}", texto
    except HTTPError as erro:
        return "IA indisponível", f"A API retornou HTTP {erro.code}. Confira a chave, o modelo e a cota."
    except (URLError, OSError, KeyError, IndexError, TypeError, ValueError):
        return "IA indisponível", "Não foi possível obter uma explicação completa nesta execução."
