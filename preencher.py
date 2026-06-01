import json
import time

import pyautogui
import pyperclip

from config import CAMPOS_FORMULARIO, COORDENADAS_PATH, VALORES_FIXOS


SELECT_FIELDS = {
    "tipo_veiculo",
    "tipo_servico",
    "perfil_transportador",
    "tipo_chave_pix",
    "ufs",
    "mesorregioes",
    "microrregioes",
    "classificacao_fiscal",
    "classificacao_fiscal_mdfe",
}

CHECKBOX_FIELDS = {
    "nao_encontrei_veiculo",
}


def _campos_por_formulario():
    campos_por_tipo = {}
    for tipo, campos in CAMPOS_FORMULARIO.items():
        todos = list(campos)
        for campo in VALORES_FIXOS.get(tipo, {}):
            if campo not in todos:
                todos.append(campo)
        campos_por_tipo[tipo] = todos
    return campos_por_tipo


COORDENADAS_PADRAO = {
    tipo: {campo: {"x": 0, "y": 0, "page": 0} for campo in campos}
    for tipo, campos in _campos_por_formulario().items()
}


def carregar_coordenadas():
    coordenadas = {
        tipo: campos.copy()
        for tipo, campos in COORDENADAS_PADRAO.items()
    }

    if not COORDENADAS_PATH.exists():
        return coordenadas

    try:
        dados = json.loads(COORDENADAS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Arquivo de coordenadas invalido: {COORDENADAS_PATH}") from exc

    for tipo, campos in dados.items():
        if tipo not in coordenadas or not isinstance(campos, dict):
            continue
        for campo, ponto in campos.items():
            if campo in coordenadas[tipo] and _ponto_valido(ponto):
                coordenadas[tipo][campo] = _normalizar_ponto(ponto)

    return coordenadas


def _ponto_valido(ponto):
    if isinstance(ponto, dict):
        return "x" in ponto and "y" in ponto
    return isinstance(ponto, (list, tuple)) and len(ponto) >= 2


def _ponto_mapeado(ponto):
    if not _ponto_valido(ponto):
        return False
    ponto = _normalizar_ponto(ponto)
    return [ponto["x"], ponto["y"]] != [0, 0]


def _normalizar_ponto(ponto):
    if isinstance(ponto, dict):
        return {
            "x": int(ponto.get("x", 0)),
            "y": int(ponto.get("y", 0)),
            "page": int(ponto.get("page", 0)),
        }

    page = int(ponto[2]) if len(ponto) > 2 else 0
    return {"x": int(ponto[0]), "y": int(ponto[1]), "page": page}


def colar_texto(texto):
    """Cola texto via clipboard, mais confiavel que digitar caractere por caractere."""
    pyperclip.copy(str(texto))
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)


def navegar_para_pagina(page):
    pyautogui.hotkey("ctrl", "home")
    time.sleep(0.5)
    for _ in range(page):
        pyautogui.press("pagedown")
        time.sleep(0.6)


def preencher_campo(campo, valor, ponto):
    pyautogui.click(ponto["x"], ponto["y"])
    time.sleep(0.3)
    if campo in CHECKBOX_FIELDS:
        time.sleep(0.3)
    elif campo in SELECT_FIELDS:
        colar_texto(valor)
        pyautogui.press("enter")
        time.sleep(0.3)
    else:
        pyautogui.hotkey("ctrl", "a")
        colar_texto(valor)


def preencher_formulario(dados, tipo_formulario):
    """Preenche os campos do formulario com os dados extraidos."""
    print(f"\nPreenchendo formulario: {tipo_formulario}")
    print("Iniciando em 3 segundos. Clique no formulario agora.")
    time.sleep(3)

    coordenadas = carregar_coordenadas().get(tipo_formulario, {})
    if not coordenadas:
        raise ValueError(f"Nenhuma coordenada configurada para {tipo_formulario!r}.")

    ordem = {
        campo: indice
        for indice, campo in enumerate(COORDENADAS_PADRAO.get(tipo_formulario, {}))
    }
    itens = []
    pendentes = []

    for campo, valor in dados.items():
        ponto = coordenadas.get(campo)
        if not _ponto_mapeado(ponto):
            pendentes.append(campo)
            print(f"  Pendente: {campo} sem coordenada mapeada")
            continue

        if campo in CHECKBOX_FIELDS:
            if valor is True or str(valor).strip().lower() in {"1", "true", "sim", "yes"}:
                itens.append((campo, valor, _normalizar_ponto(ponto)))
            continue

        if not valor:
            print(f"  Vazio: {campo} nao encontrado no documento")
            continue

        itens.append((campo, valor, _normalizar_ponto(ponto)))

    preenchidos = 0
    pagina_atual = None
    for campo, valor, ponto in sorted(
        itens,
        key=lambda item: (item[2]["page"], ordem.get(item[0], 999)),
    ):
        if ponto["page"] != pagina_atual:
            navegar_para_pagina(ponto["page"])
            pagina_atual = ponto["page"]

        preencher_campo(campo, valor, ponto)
        preenchidos += 1
        print(f"  OK: {campo}: {valor}")

    print(f"\nPreenchimento concluido. Campos preenchidos: {preenchidos}.")
    if pendentes:
        print(
            "Campos sem coordenada: "
            + ", ".join(pendentes)
            + f". Rode: python mapear_coordenadas.py {tipo_formulario}"
        )
