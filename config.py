import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
ENV_PATH = PROJECT_DIR / ".env"
COORDENADAS_PATH = PROJECT_DIR / "coordenadas.json"


def _carregar_env_local():
    if not ENV_PATH.exists():
        return

    for linha in ENV_PATH.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(chave, valor)


_carregar_env_local()

# Configure a chave no Windows com:
# setx GEMINI_API_KEY "sua-chave"
# Ou crie um arquivo .env local com GEMINI_API_KEY=sua-chave
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

# Monitores do mss:
# 0 = area virtual com todos os monitores
# 1..N = monitores individuais
MONITOR_DOCUMENTO = int(os.getenv("MONITOR_DOCUMENTO", "1"))
MONITOR_FORMULARIO = int(os.getenv("MONITOR_FORMULARIO", "2"))

VALORES_FIXOS = {
    "veiculo": {
        "tipo_veiculo": "Plataforma 5mts",
        "nao_encontrei_veiculo": True,
        "classificacao_fiscal": "TAC Independente",
    },
    "transportadora": {
        "tipo_servico": "Ambos",
        "perfil_transportador": "TAC Independente",
        "tipo_chave_pix": "CPF/CNPJ",
        "complemento": "",
        "ufs": "",
        "mesorregioes": "",
        "microrregioes": "",
        "valor_saida": "200,00",
        "valor_km_rodado": "3,5",
        "valor_saida_pesados": "0",
        "valor_km_carga_maxima": "0",
        "rntrc": "",
        "classificacao_fiscal_mdfe": "TAC",
    },
}

CAMPOS_FORMULARIO = {
    "motorista": [
        "cpf",
        "nome",
        "email",
        "celular",
        "data_validade",
    ],
    "veiculo": [
        "tipo_veiculo",
        "nao_encontrei_veiculo",
        "marca",
        "modelo",
        "ano",
        "placa",
        "renavam",
        "qtd_eixos",
        "classificacao_fiscal",
        "data_validade",
    ],
    "transportadora": [
        "cpf_cnpj",
        "nome",
        "email",
        "celular",
        "nome_local",
        "cidade_atuacao",
        "chave_pix",
        "titular_conta",
        "cpf_cnpj_titular",
        "cep",
        "numero",
        "logradouro",
        "bairro",
        "municipio",
        "uf",
    ],
}
