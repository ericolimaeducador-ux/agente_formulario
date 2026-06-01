import json
import sys
import time

import pyautogui

from config import CAMPOS_FORMULARIO, COORDENADAS_PATH


def carregar_existente():
    if not COORDENADAS_PATH.exists():
        return {}
    return json.loads(COORDENADAS_PATH.read_text(encoding="utf-8"))


def salvar_coordenadas(dados):
    COORDENADAS_PATH.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def escolher_tipo():
    if len(sys.argv) > 1:
        tipo = sys.argv[1].strip().lower()
        if tipo in CAMPOS_FORMULARIO:
            return tipo
        raise SystemExit(
            f"Formulario invalido: {tipo}. Opcoes: {', '.join(CAMPOS_FORMULARIO)}"
        )

    print("Escolha o formulario para mapear:")
    tipos = list(CAMPOS_FORMULARIO)
    for indice, tipo in enumerate(tipos, start=1):
        print(f"{indice}. {tipo}")

    escolha = input("Numero: ").strip()
    try:
        return tipos[int(escolha) - 1]
    except (ValueError, IndexError) as exc:
        raise SystemExit("Opcao invalida.") from exc


def main():
    tipo = escolher_tipo()
    campos = CAMPOS_FORMULARIO[tipo]

    print("=" * 50)
    print("MAPEADOR DE COORDENADAS")
    print("=" * 50)
    print(f"Formulario: {tipo}")
    print("\nInstrucoes:")
    print("1. Abra o formulario no monitor correto.")
    print("2. Posicione o mouse em cima de cada campo pedido.")
    print("3. Aguarde a captura automatica.")
    print("4. As coordenadas serao salvas em coordenadas.json.")
    print("\nIniciando em 5 segundos. Pressione Ctrl+C para parar.\n")
    time.sleep(5)

    coordenadas = carregar_existente()
    coordenadas.setdefault(tipo, {})

    for campo in campos:
        print(f"Posicione o mouse no campo: {campo}")
        time.sleep(4)
        x, y = pyautogui.position()
        coordenadas[tipo][campo] = [x, y]
        salvar_coordenadas(coordenadas)
        print(f'  "{campo}": [{x}, {y}]')
        print()

    print(f"Mapeamento concluido: {COORDENADAS_PATH}")


if __name__ == "__main__":
    main()
