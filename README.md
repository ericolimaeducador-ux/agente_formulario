# Agente de formulario

Automatiza a leitura de um documento em uma tela e o preenchimento de um formulario em outra tela.

## Configuracao

1. Instale as dependencias:

```powershell
pip install -r requirements.txt
```

2. Configure a chave do Gemini em uma variavel de ambiente:

```powershell
setx GEMINI_API_KEY "sua-chave"
```

Ou copie `.env.example` para `.env` e preencha `GEMINI_API_KEY`.

3. Ajuste os monitores, se necessario:

```env
MONITOR_DOCUMENTO=1
MONITOR_FORMULARIO=2
```

## Mapear campos

Antes de preencher automaticamente, mapeie as coordenadas do formulario:

```powershell
python mapear_coordenadas.py motorista
python mapear_coordenadas.py veiculo
python mapear_coordenadas.py transportadora
```

O arquivo `coordenadas.json` sera criado automaticamente.

## Rodar

Interface flutuante:

```powershell
python interface.py
```

Execucao direta:

```powershell
python main.py
```
