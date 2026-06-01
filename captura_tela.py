import base64
import io

import mss
from PIL import Image


def listar_monitores():
    with mss.mss() as sct:
        return list(sct.monitors)


def capturar_monitor(monitor_index):
    """Captura screenshot de um monitor especifico e retorna PNG em base64."""
    with mss.mss() as sct:
        monitores = sct.monitors
        if monitor_index < 0 or monitor_index >= len(monitores):
            disponiveis = ", ".join(str(i) for i in range(len(monitores)))
            raise ValueError(
                f"Monitor {monitor_index} nao encontrado. Disponiveis: {disponiveis}."
            )

        monitor = monitores[monitor_index]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def detectar_tipo_documento(img_base64):
    """Mantido por compatibilidade; a analise real e feita pelo Gemini."""
    return img_base64
