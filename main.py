import sys

from captura_tela import capturar_monitor
from config import CAMPOS_FORMULARIO, MONITOR_DOCUMENTO, MONITOR_FORMULARIO, VALORES_FIXOS
from gemini_ler import extrair_dados, identificar_formulario
from preencher import preencher_formulario


def preparar_dados(tipo_formulario, dados):
    if tipo_formulario == "transportadora":
        cpf_cnpj = dados.get("cpf_cnpj", "")
        nome = dados.get("nome", "")

        if not dados.get("chave_pix"):
            dados["chave_pix"] = cpf_cnpj
        dados["titular_conta"] = nome
        dados["cpf_cnpj_titular"] = cpf_cnpj

    for campo, valor in VALORES_FIXOS.get(tipo_formulario, {}).items():
        if valor not in ("", None):
            dados[campo] = valor

    return dados


def main():
    print("=" * 50)
    print("AGENTE DE PREENCHIMENTO AUTOMATICO")
    print("=" * 50)

    try:
        print("\nCapturando telas...")
        img_tela1 = capturar_monitor(MONITOR_DOCUMENTO)
        img_tela2 = capturar_monitor(MONITOR_FORMULARIO)
        print("Telas capturadas.")

        print("\nIdentificando formulario na tela do formulario...")
        tipo_formulario = identificar_formulario(img_tela2)
        if tipo_formulario not in CAMPOS_FORMULARIO:
            raise ValueError(f"Formulario nao suportado: {tipo_formulario!r}.")
        print(f"Formulario identificado: {tipo_formulario.upper()}")

        print("\nExtraindo dados do documento...")
        dados = extrair_dados(img_tela1, tipo_formulario)
        print("Dados extraidos:")
        for campo, valor in dados.items():
            print(f"   {campo}: {valor}")

        print("\nAplicando regras e valores fixos...")
        dados = preparar_dados(tipo_formulario, dados)

        preencher_formulario(dados, tipo_formulario)
        return 0
    except Exception as exc:
        print(f"\nERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
