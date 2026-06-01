import base64
import json

from google import genai
from google.genai import types

from config import CAMPOS_FORMULARIO, GEMINI_API_KEY, GEMINI_MODEL


TIPOS_FORMULARIO = set(CAMPOS_FORMULARIO)
_CLIENT = None


def _obter_cliente():
    global _CLIENT
    if _CLIENT is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY nao configurada. Defina a variavel de ambiente "
                "ou crie um arquivo .env com GEMINI_API_KEY=sua-chave."
            )

        _CLIENT = genai.Client(api_key=GEMINI_API_KEY)

    return _CLIENT


def _gerar_com_imagem(img_data, prompt):
    cliente = _obter_cliente()
    return cliente.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=img_data, mime_type="image/png"),
            prompt,
        ],
    )


def _limpar_json(texto):
    texto = (texto or "").strip()
    if not texto:
        raise ValueError("Gemini retornou uma resposta vazia.")

    if "```json" in texto:
        texto = texto.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in texto:
        texto = texto.split("```", 1)[1].split("```", 1)[0]

    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio != -1 and fim != -1 and fim > inicio:
        texto = texto[inicio : fim + 1]

    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        amostra = texto[:300].replace("\n", " ")
        raise ValueError(f"Gemini nao retornou JSON valido: {amostra}") from exc


def _filtrar_campos(dados, tipo_formulario):
    campos = CAMPOS_FORMULARIO.get(tipo_formulario, [])
    return {campo: dados.get(campo, "") for campo in campos}


def identificar_formulario(img_base64_tela2):
    """Le o cabecalho da tela 2 e identifica o formulario aberto."""
    img_data = base64.b64decode(img_base64_tela2)

    response = _gerar_com_imagem(
        img_data,
        """Olhe o cabecalho desta tela e responda APENAS com uma dessas palavras:
            - motorista (Cadastro de Motorista)
            - veiculo (Cadastro de Veiculo)
            - transportadora (Cadastro de Transportadora)
            Nao escreva explicacao.""",
    )

    texto = (response.text or "").strip().lower()
    for tipo in TIPOS_FORMULARIO:
        if texto == tipo or tipo in texto:
            return tipo

    raise ValueError(
        f"Formulario nao reconhecido pelo Gemini: {texto!r}. "
        f"Esperado: {', '.join(sorted(TIPOS_FORMULARIO))}."
    )


def extrair_dados(img_base64_tela1, tipo_formulario):
    """Extrai dados do documento na tela 1 conforme o formulario necessario."""
    if tipo_formulario not in TIPOS_FORMULARIO:
        raise ValueError(f"Tipo de formulario invalido: {tipo_formulario!r}.")

    img_data = base64.b64decode(img_base64_tela1)

    prompts = {
        "motorista": """Analise este documento e extraia em JSON:
            {
                "cpf": "",
                "nome": "",
                "email": "",
                "celular": "",
                "data_validade": ""
            }
            Retorne APENAS o JSON.""",
        "veiculo": """Analise este CRLV e extraia em JSON:
            {
                "marca": "",
                "modelo": "",
                "ano": "",
                "placa": "",
                "renavam": "",
                "qtd_eixos": "",
                "data_validade": ""
            }
            data_validade deve ser a data de validade/vencimento do CRLV que aparece no documento.
            Retorne data_validade no formato dd/mm/aaaa quando possivel.
            Retorne APENAS o JSON.""",
        "transportadora": """Analise este documento e extraia em JSON:
            {
                "cpf_cnpj": "",
                "nome": "",
                "email": "",
                "celular": "",
                "nome_local": "",
                "cidade_atuacao": "",
                "chave_pix": "",
                "titular_conta": "",
                "cpf_cnpj_titular": "",
                "cep": "",
                "numero": "",
                "logradouro": "",
                "bairro": "",
                "municipio": "",
                "uf": ""
            }
            Extraia cidade_atuacao do campo endereco.
            chave_pix deve ser igual ao cpf_cnpj.
            titular_conta deve ser igual ao nome quando nao houver titular especifico.
            cpf_cnpj_titular deve ser igual ao cpf_cnpj quando nao houver titular especifico.
            Retorne APENAS o JSON.""",
    }

    response = _gerar_com_imagem(img_data, prompts[tipo_formulario])

    dados = _limpar_json(response.text)
    if not isinstance(dados, dict):
        raise ValueError("Gemini retornou JSON, mas o valor principal nao e um objeto.")

    return _filtrar_campos(dados, tipo_formulario)
